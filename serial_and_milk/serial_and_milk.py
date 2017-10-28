from ast import literal_eval # For interpreting module data
from time import sleep       # For delays

import serial                # For reading in a serial device
import pynmea2               # For reading NMEA 0183 sentences
import multiprocessing       # For multiprocessing in Python

com_queue = multiprocessing.Queue()

def print_nmea(telemetry):
    print "Latitude: {}".format(telemetry.latitude)
    print "Longitude: {}".format(telemetry.longitude)
    print "Altitude: {}\n".format(telemetry.altitude)

def read_com_port(com_port, com_queue):
    with serial.Serial(com_port, baudrate = 9600, timeout = 0.5) as ser:

        # Flushing any prior content within serial buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        while True:
            try:
                if (ser.isOpen() == False):
                    ser.open()
                    
                raw_sentence = ser.readline().decode('ascii', errors = 'replace') # Reads serial data
        
                telemetry = pynmea2.parse(raw_sentence) # Parses data

                while not com_queue.empty():
                    com_queue.get_nowait()
                
                com_queue.put(telemetry)
            except Exception as e:
                print e
                ser.close()                # Closes the serial port

def read_from_queue():
    return com_queue.get()

if __name__ == '__main__':
    com_port = raw_input("Enter a COM port to listen to: ")
    
    print "Initialising Serial and Milk..."         # Prints out raw values

    p = multiprocessing.Process(target=read_com_port, args=(com_port,com_queue,))
    p.start()

    while True:
        try:
            telemetry = read_from_queue()
            print_nmea(telemetry)
            sleep(2)
        except Exception as e:
            print e
            ser.close()

            # Handling closing multiprocessing stuff
            com_queue.close()
            com_queue.join_thread()
            p.join()
                
