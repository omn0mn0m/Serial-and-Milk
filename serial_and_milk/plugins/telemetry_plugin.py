import logging
import multiprocessing       # For multiprocessing in Python
import serial                # For reading in a serial device

import pynmea2               # For reading NMEA 0183 sentences

from Tkinter import *

from plugin import Plugin

class TelemetryPlugin(Plugin):

    def __init__(self, baudrate, out_queue):
        logging.basicConfig(filename='telemetry.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("-------------- Start of Log -----------------------")

        port_file = open("port.txt", "r")
        self.com_port = port_file.read().strip()

        in_queue = multiprocessing.Queue()
        super(TelemetryPlugin, self).__init__(self.com_port, baudrate, in_queue, out_queue)

    def process_data(self, raw_data):
        raw_data = raw_data.strip('[]')

        try:
            telemetry = pynmea2.parse(raw_data) # Parses data
        except:
            telemetry = raw_data

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
                
                self.out_queue.put(telemetry.altitude)
            except:
                print "Error"

        self.after_id = master.after(1000, self.update_gui, master, nmea_val, time_val, lat_val, long_val, alt_val)

    def load_gui(self, master):
        nmea_val = StringVar()
        time_val = StringVar()
        lat_val = StringVar()
        long_val = StringVar()
        alt_val = StringVar()

        frame = Frame(master)

        Label(frame, text='Raw NMEA').pack(pady=5,padx=50)
        Label(frame, textvariable=nmea_val).pack(pady=5, padx=50)

        Label(frame, text='Time Stamp').pack(pady=5,padx=50)
        Label(frame, textvariable=time_val).pack(pady=5, padx=50)

        Label(frame, text='Latitude').pack(pady=5,padx=50)
        Label(frame, textvariable=lat_val).pack(pady=5, padx=50)

        Label(frame, text='Longitude').pack(pady=5,padx=50)
        Label(frame, textvariable=long_val).pack(pady=5, padx=50)

        Label(frame, text='Altitude').pack(pady=5,padx=50)
        Label(frame, textvariable=alt_val).pack(pady=5, padx=50)

        master.add(frame, text="Telemetry")

        self.after_id = master.after(1000, self.update_gui, master, nmea_val, time_val, lat_val, long_val, alt_val)

    def close(self, master):
        logging.debug("\n")
        
        master.after_cancel(self.after_id)
        super(TelemetryPlugin, self).close()
