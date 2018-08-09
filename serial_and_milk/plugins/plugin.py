import multiprocessing       # For multiprocessing in Python
import serial                # For reading in a serial device

class Plugin(object):

    def __init__(self, com_port, baudrate, in_queue=None, out_queue=None):
        self.TIMEOUT = 10
        self.baudrate = baudrate
        self.com_port = com_port
        self.out_queue = out_queue
        self.in_queue = in_queue
        self.p = multiprocessing.Process(target=self.periodic)
        self.p.start()

    # Requires implementation in subclass
    def update_gui(self): raise NotImplementedError()
    def load_gui(self): raise NotImplementedError()

    # Methods
    def read_from_queue(self):
        read_timeout = 0
        
        while self.in_queue.empty():
            if read_timeout > self.TIMEOUT:
                print "Queue empty..."
                return None

            read_timeout += 1

        return self.in_queue.get()
        
    def write_to_queue(self, value):
        if not self.out_queue == None:
            self.out_queue.put(value)

    def periodic(self):
        if not (self.com_port == "---"):
            with serial.Serial(self.com_port, baudrate = self.baudrate, timeout = 0.5) as ser:
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

                        raw_data = ''

                        while not (message_byte == '\n'):
                            raw_data += message_byte
                            message_byte = ser.read()

                        raw_data = raw_data.decode('ascii', errors='replace')

                        data = self.process_data(raw_data)

                        while not self.in_queue.empty():
                            self.in_queue.get_nowait()

                        self.in_queue.put(data)
                    except Exception as e:
                        print e
                        break

    def process_data(self, raw_data):
        print raw_data

        return raw_data

    def close(self):
        self.in_queue.close()
        self.in_queue.join_thread()

        self.p.terminate()
