from time import sleep       # For delays

import serial                # For reading in a serial device
import multiprocessing       # For multiprocessing in Python

from Tkinter import *
import tkMessageBox

from telemetry_plugin import Telemetry_Plugin

def do_nothing():
    pass

def read_com_port(com_port, telemetry_plugin):
    if not (com_port == "---"):
        with serial.Serial(com_port, baudrate = 9600, timeout = 0.5) as ser:
            
            # Flushing any prior content within serial buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Getting rid of weird looking data
            for i in range(10):
                ser.readline()
                
            while True:
                try:
                    if (ser.isOpen() == False):
                        ser.open()
                    
                    message_byte = ser.read()
                    
                    telemetry = telemetry_plugin.process_message(ser, message_byte)
                        
                    while not telemetry_plugin.com_queue.empty():
                        telemetry_plugin.com_queue.get_nowait()
                            
                    telemetry_plugin.com_queue.put(telemetry)
                except Exception as e:
                    print e
                    break

def start_serial_read(telemetry_plugin):
    port_file = open("port.txt", "r")
    com_port = port_file.read().strip()

    com_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=read_com_port, args=(com_port,telemetry_plugin))
    p.start()

if __name__ == '__main__':
    port_file = open("port.txt", "r")
    com_port = port_file.read().strip()

    com_queue = multiprocessing.Queue()
    telemetry_plugin = Telemetry_Plugin(com_queue)
    
    p = multiprocessing.Process(target=read_com_port, args=(com_port,telemetry_plugin))
    p.start()
    
    master = Tk()
    master.title("Serial and Milk")
    master.geometry("720x320")

    menubar = Menu(master)
    
    file_menu = Menu(menubar, tearoff = 0)
    file_menu.add_command(label = "New", command = do_nothing)
    file_menu.add_command(label = "Open", command = do_nothing)
    file_menu.add_command(label = "Save", command = do_nothing)
    file_menu.add_separator()
    file_menu.add_command(label = "Change Port", command = do_nothing)
    file_menu.add_command(label = "Reset Serial", command = lambda: start_serial_read(telemetry_plugin))
    file_menu.add_separator()
    file_menu.add_command(label = "Exit", command = master.quit)

    help_menu = Menu(menubar, tearoff = 0)
    help_menu.add_command(label = "About", command = do_nothing)
    help_menu.add_command(label = "GitHub", command = do_nothing)
    
    menubar.add_cascade(label = "File", menu = file_menu)
    menubar.add_cascade(label = "Help", menu = help_menu)
    
    master.config(menu = menubar)

    telemetry_plugin.load(master)
    
    master.mainloop()

    # Handling closing multiprocessing stuff
    com_queue.close()
    com_queue.join_thread()
    p.terminate()
    logging.debug("\n")
