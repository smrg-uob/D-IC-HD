from cameras.CameraList import CameraList
from gui.Gui import Gui

gui = Gui(CameraList().scan_cameras())
gui.launch_gui()
