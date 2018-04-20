import logging
import multiprocessing
import serial

from Tkinter import *
from ttk import *

from plugin import Plugin

# Plugin specific imports
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib import style

class PlottingPlugin():

    def __init__(self, baudrate):
        style.use('ggplot')
        
        self.xar = []
        self.yar = []

    def process_data(self, raw_data):
        pass

    def update_gui(self, master):
        pass

    def load_gui(self, master):
        frame = Frame(master)

        fig = plt.figure(figsize=(14, 4.5), dpi=100)

        self.ax = fig.add_subplot(1,1,1)
        self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot(self.xar, self.yar)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        ani = animation.FuncAnimation(fig, self.animate, interval=1000)
        
        canvas.draw()
        frame.pack()
        
        master.add(frame, text="Plotting")

    def close(self):
        pass

    def animate(self, i):
        try:
            self.yar.append(99-i)
            self.xar.append(i)
            self.line.set_data(self.xar, self.yar)
            self.ax.set_xlim(0, i+1)
        except:
            print "Plotting plugin error"