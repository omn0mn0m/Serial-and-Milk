from time import sleep       # For delays

import serial                # For reading in a serial device
import multiprocessing       # For multiprocessing in Python

from Tkinter import *
from ttk import Notebook
import tkMessageBox

from plugins.telemetry_plugin import Telemetry_Plugin

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

if __name__ == '__main__':
    port_file = open("port.txt", "r")
    com_port = port_file.read().strip()
    
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
    file_menu.add_separator()
    file_menu.add_command(label = "Exit", command = master.quit)

    help_menu = Menu(menubar, tearoff = 0)
    help_menu.add_command(label = "About", command = do_nothing)
    help_menu.add_command(label = "GitHub", command = do_nothing)
    
    menubar.add_cascade(label = "File", menu = file_menu)
    menubar.add_cascade(label = "Help", menu = help_menu)
    
    master.config(menu = menubar)

    notebook = Notebook(master)
    notebook.pack(fill=BOTH, expand=1)

    # ================ Plugin Setup ====================
    # Setup plugin processes
    plugin_list = ['telemetry']
    plugin_queues = {}

    for plugin in plugin_list:
        plugin_queues[plugin] = multiprocessing.Queue()
    
    telemetry_plugin = Telemetry_Plugin(plugin_queues['telemetry'])
    p = multiprocessing.Process(target=read_com_port, args=(com_port,telemetry_plugin))
    p.start()

    # Load GUI elemenets of plugins
    telemetry_plugin.load(notebook)
    # ==================================================
    
    master.mainloop()

    # Handling closing multiprocessing stuff
    for plugin in plugin_list:
        plugin_queues[plugin].close()
        plugin_queues[plugin].join_thread()
        
    p.terminate()
