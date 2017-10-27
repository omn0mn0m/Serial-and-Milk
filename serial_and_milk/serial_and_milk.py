from ast import literal_eval # For interpreting module data
from time import sleep       # For delays

import serial                # For reading in a serial device
import pynmea2               # For reading NMEA 0183 sentences

def print_nmea(telemetry):
    print "Latitude: {}".format(telemetry.latitude)
    print "Longitude: {}".format(telemetry.longitude)
    print "Altitude: {}\n".format(telemetry.altitude)

com_port = raw_input("Enter a COM port to listen to: ")

print "Initialising Serial and Milk..."         # Prints out raw values

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
            print_nmea(telemetry)
            
            sleep(0.0)                              # To avoid reading too fast
        except Exception as e:
            print e
            # Closes the serial port
            ser.close()
