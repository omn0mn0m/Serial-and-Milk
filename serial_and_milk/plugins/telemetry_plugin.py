import logging
import multiprocessing       # For multiprocessing in Python

import pynmea2               # For reading NMEA 0183 sentences

from Tkinter import *
from ttk import Notebook
import tkMessageBox

class TelemetryPlugin:
    
    def __init__(self):
        logging.basicConfig(filename='telemetry.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.debug("-------------- Start of Log -----------------------")

        self.com_queue = com_queue
        self.TIMEOUT = 10
        self.read_timeout = 0

        self.com_queue = multiprocessing.Queue()
        self.p = multiprocessing.Process(target=read_com_port, args=(com_port))
        self.p.start()

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

    def read_com_port(self, com_port):
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

                        telemetry = self.process_message(ser, message_byte)

                        while not self..com_queue.empty():
                            self..com_queue.get_nowait()

                        self..com_queue.put(telemetry)
                    except Exception as e:
                        print e
                        break

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

        master.after(1000, self.update_gui, master, nmea_val, time_val, lat_val, long_val, alt_val)

    def close(self):
        logging.debug("\n")
        
        self.com_queue.close()
        self.com_queue.join_thread()

        self.p.terminate()
