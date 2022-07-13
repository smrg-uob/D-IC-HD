import matplotlib
from gui.Gui import Gui

# Make sure to use the 'Agg' backend in matplotlib
# we strictly do not want 'tkAgg' as we're not using it
# if we do not specify this, matplotlib will default to 'tkAgg' when importing matplotlib.pyplot from tkinter
# if matplotlib uses the 'tkAgg' backend, it will interfere with our tkinter windows when manipulating figures
matplotlib.use("Agg")

# Launch the gui
gui = Gui()
gui.launch_gui()


def log(msg):
    gui.log(msg)
