from Tkinter import *
from ttk import Notebook
import tkMessageBox

from plugins.telemetry_plugin import TelemetryPlugin
from plugins.plotting_plugin import PlottingPlugin

def do_nothing():
    pass

if __name__ == '__main__':
    master = Tk()
    master.protocol('WM_DELETE_WINDOW', master.quit)
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
    telemetry_plugin = TelemetryPlugin(baudrate=9600)
    telemetry_plugin.load_gui(notebook)

    plotting_plugin = PlottingPlugin(baudrate=9600)
    plotting_plugin.load_gui(notebook)
    
    
    # ==================================================
    
    master.mainloop()
    
    telemetry_plugin.close(master)
    plotting_plugin.close()