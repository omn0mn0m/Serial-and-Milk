import logging
import pynmea2               # For reading NMEA 0183 sentences

from Tkinter import *
import tkMessageBox

class Telemetry_Plugin:
    
    def __init__(self, com_queue):
        logging.basicConfig(filename='telemetry.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("-------------- Start of Log -----------------------")

        self.com_queue = com_queue
        self.TIMEOUT = 10
        self.read_timeout = 0

    def print_nmea(self, telemetry):
        print "Latitude: {} ".format(telemetry.latitude)
        print "Longitude: {} ".format(telemetry.longitude)
        print "Altitude: {}\n".format(telemetry.altitude)

    def read_from_queue(self):
        while self.com_queue.empty():
            if self.read_timeout > self.TIMEOUT:
                print "Queue empty..."
                self.read_timeout = 0
                return None

            self.read_timeout += 1
    #        print read_timeout

        self.read_timeout = 0
        return self.com_queue.get()

    def process_message(self, ser, message_byte):
        raw_sentence = ''
        
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

        return telemetry

    def update_gui(self, master, nmea_val, time_val, lat_val, long_val, alt_val):
        telemetry = self.read_from_queue()

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

        master.after(1000, self.update_gui, master, nmea_val, time_val, lat_val, long_val, alt_val)

    def load(self, master):
        nmea_val = StringVar()
        time_val = StringVar()
        lat_val = StringVar()
        long_val = StringVar()
        alt_val = StringVar()

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

        master.after(1000, self.update_gui, master, nmea_val, time_val, lat_val, long_val, alt_val)
