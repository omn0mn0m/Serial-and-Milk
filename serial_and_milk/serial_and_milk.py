from ast import literal_eval # For interpreting module data
from time import sleep       # For delays

import serial                # For reading in a serial device
import pynmea2               # For reading NMEA 0183 sentences
import multiprocessing       # For multiprocessing in Python
import logging

from Tkinter import *
import tkMessageBox

TIMEOUT = 10

def do_nothing():
    pass

def print_nmea(telemetry):
    print "Latitude: {} ".format(telemetry.latitude)
    print "Longitude: {} ".format(telemetry.longitude)
    print "Altitude: {}\n".format(telemetry.altitude)

logging.basicConfig(filename='telemetry.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.debug("-------------- Start of Log -----------------------")

def read_com_port(com_port, com_queue):
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
                    
                    raw_sentence = ''
                    message_byte = ser.read()
                    
                    while not (message_byte == '\n'):
                        raw_sentence += message_byte
                        message_byte = ser.read()
                        
                    raw_sentence = raw_sentence.decode('ascii', errors='replace').strip('[]')
                    print raw_sentence
                    
                    try:
                        telemetry = pynmea2.parse(raw_sentence) # Parses data
                    except:
                        telemetry = raw_sentence
                        
                    logging.info("%s", telemetry)
                        
                    while not com_queue.empty():
                        com_queue.get_nowait()
                            
                    com_queue.put(telemetry)
                except Exception as e:
                    print e
                    break

read_timeout = 0
                    
def read_from_queue():
    while com_queue.empty():
        global read_timeout
        
        if read_timeout > TIMEOUT:
            print "Queue empty..."
            read_timeout = 0
            return None
        
        read_timeout += 1
#        print read_timeout

    read_timeout = 0
    return com_queue.get()

def start_serial_read():
    port_file = open("port.txt", "r")
    com_port = port_file.read().strip()

    com_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=read_com_port, args=(com_port,com_queue,))
    p.start()

def update_labels(master, nmea_val, time_val, lat_val, long_val, alt_val):
    telemetry = read_from_queue()

    if not telemetry == None:
        nmea_val.set(telemetry)
        
        try:
            data_time = telemetry.timestamp
            time_val.set(data_time.strftime("%X"))
            lat_val.set(telemetry.latitude)
            long_val.set(telemetry.longitude)
            alt_val.set(telemetry.altitude)
        except:
            time_val.set("error")
            lat_val.set("error")
            long_val.set("error")
            alt_val.set("error")

    master.after(1000, update_labels, master, nmea_val, time_val, lat_val, long_val, alt_val)

def load_telemetry(master, nmea_val, time_val, lat_val, long_val, alt_val):
    Label(master, text='Raw NMEA').pack(pady=5,padx=50)
    
    Label(master, textvariable=nmea_val).pack(pady=5, padx=50)

    Label(master, text='Time Stamp').pack(pady=5,padx=50)
    
    Label(master, textvariable=time_val).pack(pady=5, padx=50)

    Label(master, text='Latitude').pack(pady=5,padx=50)
    
    Label(master, textvariable=lat_val).pack(pady=5, padx=50)
    
    Label(master, text='Longitude').pack(pady=5,padx=50)
    
    Label(master, textvariable=long_val).pack(pady=5, padx=50)
    
    Label(master, text='Altitude').pack(pady=5,padx=50)
    
    Label(master, textvariable=alt_val).pack(pady=5, padx=50)

    master.after(1000, update_labels, master, nmea_val, time_val, lat_val, long_val, alt_val)
    

if __name__ == '__main__':
    port_file = open("port.txt", "r")
    com_port = port_file.read().strip()

    com_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=read_com_port, args=(com_port,com_queue,))
    p.start()
    
    master = Tk()
    master.title("Serial and Milk - Telemetry Mode")
    master.geometry("720x320")

    menubar = Menu(master)
    
    file_menu = Menu(menubar, tearoff = 0)
    file_menu.add_command(label = "New", command = do_nothing)
    file_menu.add_command(label = "Open", command = do_nothing)
    file_menu.add_command(label = "Save", command = do_nothing)
    file_menu.add_separator()
    file_menu.add_command(label = "Change Port", command = do_nothing)
    file_menu.add_command(label = "Reset Serial", command = start_serial_read)
    file_menu.add_separator()
    file_menu.add_command(label = "Exit", command = master.quit)

    help_menu = Menu(menubar, tearoff = 0)
    help_menu.add_command(label = "About", command = do_nothing)
    help_menu.add_command(label = "GitHub", command = do_nothing)
    
    menubar.add_cascade(label = "File", menu = file_menu)

    nmea_val = StringVar()
    time_val = StringVar()
    lat_val = StringVar()
    long_val = StringVar()
    alt_val = StringVar()

    load_telemetry(master, nmea_val, time_val, lat_val, long_val, alt_val)

    menubar.add_cascade(label = "Help", menu = help_menu)
    master.config(menu = menubar)
   
    master.mainloop()

    # Handling closing multiprocessing stuff
    com_queue.close()
    com_queue.join_thread()
    p.terminate()
    logging.debug("\n")
