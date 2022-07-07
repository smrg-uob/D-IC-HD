from CameraElement import CameraElement
from datetime import date, datetime
from xvh.d_ic_hd.cameras.CameraList import CameraList
import Tkinter as Tk


class Gui:
    def launch_gui(self):
        self.log("DI-C-HD Launched Successfully")
        self.gui.mainloop()

    def on_press(self):
        self.camera_1.refresh_image()
        self.camera_2.refresh_image()

    def log(self, line):
        self.console.configure(state="normal")
        self.console.insert(Tk.END, "[" + str(date.today()) + "][" + datetime.now().strftime("%H:%M:%S") + "] " + line + '\n')
        self.console.configure(state="disabled")

    def __init__(self):
        # Create the gui window
        self.gui = Tk.Tk()
        self.gui.wm_title("ICHD-DIC")

        # Set full screen
        self.gui.state('zoomed')

        # sub-frame dimensions
        w_inputs = 300

        # Create frames for the inputs and outputs
        self.frm_input = Tk.Frame(master=self.gui, width=w_inputs, relief=Tk.GROOVE, borderwidth=3)
        self.frm_output = Tk.Frame(master=self.gui, relief=Tk.GROOVE, borderwidth=3)
        self.frm_input.pack(fill=Tk.BOTH, side=Tk.LEFT, expand=False)
        self.frm_output.pack(fill=Tk.BOTH, side=Tk.LEFT, expand=True)
        # Prevent frame size resetting after adding widgets
        self.frm_input.pack_propagate(False)

        # For the output frame, create sub-frames for the cameras, and for the console
        self.frm_cameras = Tk.Frame(master=self.frm_output)
        self.frm_console = Tk.Frame(master=self.frm_output, relief=Tk.GROOVE, borderwidth=3)
        self.frm_output.grid_rowconfigure(0, weight=100)
        self.frm_output.grid_rowconfigure(1, weight=1)
        self.frm_output.grid_columnconfigure(0, weight=1)
        self.frm_cameras.grid(row=0, column=0, sticky=(Tk.N, Tk.W, Tk.E, Tk.S))
        self.frm_console.grid(row=1, column=0, sticky=(Tk.W, Tk.E))

        # Create the console
        self.console = Tk.Text(master=self.frm_console, height=10)
        self.console_scroll = Tk.Scrollbar(master=self.frm_console, orient=Tk.VERTICAL, command=self.console.yview)
        self.frm_console.grid_columnconfigure(0, weight=1)
        self.console.grid(row=0, column=0, sticky=(Tk.N, Tk.W, Tk.E, Tk.S))
        self.console_scroll.grid(row=0, column=1, sticky=(Tk.N, Tk.S))
        self.console['yscrollcommand'] = self.console_scroll.set
        self.console.configure(state="disabled")

        # Fetch available cameras
        self.cameras = CameraList(self.log).scan_cameras()

        # Create the camera elements
        self.camera_1 = CameraElement(self.frm_cameras, "CAM 1", self.cameras.create_camera(0), self.log)
        self.camera_2 = CameraElement(self.frm_cameras, "CAM 2", self.cameras.create_camera(1), self.log)

        # Add a test button to take a new image
        self.btn_1 = Tk.Button(master=self.frm_input, text="Test", command=lambda: self.on_press())
        self.btn_1.pack(ipadx=5, ipady=5, expand=True)
