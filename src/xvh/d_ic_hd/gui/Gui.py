from CameraElement import CameraElement
from datetime import date, datetime
from xvh.d_ic_hd.cameras.CameraList import CameraList
import Tkinter as tk


class Gui:
    def __init__(self):
        # Create the gui window
        self.gui = tk.Tk()
        self.gui.wm_title("ICHD-DIC")

        # Set full screen
        self.gui.state('zoomed')

        # sub-frame dimensions
        w_inputs = 300

        # Create frames for the inputs and outputs
        self.frm_input = tk.Frame(master=self.gui, width=w_inputs, relief=tk.GROOVE, borderwidth=3)
        self.frm_output = tk.Frame(master=self.gui, relief=tk.GROOVE, borderwidth=3)
        self.frm_input.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        self.frm_output.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # Prevent frame size resetting after adding widgets
        self.frm_input.pack_propagate(False)

        # For the output frame, create sub-frames for the cameras, and for the console
        self.frm_cameras = tk.Frame(master=self.frm_output)
        self.frm_console = tk.Frame(master=self.frm_output, relief=tk.GROOVE, borderwidth=3)
        self.frm_output.grid_rowconfigure(0, weight=100)
        self.frm_output.grid_rowconfigure(1, weight=1)
        self.frm_output.grid_columnconfigure(0, weight=1)
        self.frm_cameras.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.frm_console.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Create the console
        self.console = tk.Text(master=self.frm_console, height=10)
        self.console_scroll = tk.Scrollbar(master=self.frm_console, orient=tk.VERTICAL, command=self.console.yview)
        self.frm_console.grid_columnconfigure(0, weight=1)
        self.console.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.console_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.console['yscrollcommand'] = self.console_scroll.set
        self.console.configure(state="disabled")

        # Fetch available cameras
        self.cameras = CameraList(self.log).scan_cameras()

        # Create the camera elements
        self.camera_1 = CameraElement(tk, self.frm_cameras, "CAM 1", self.cameras, 0, self.log)
        self.camera_2 = CameraElement(tk, self.frm_cameras, "CAM 2", self.cameras, 1, self.log)

    def launch_gui(self):
        self.log("DI-C-HD Launched Successfully")
        self.gui.mainloop()

    def log(self, line):
        # enable the text box
        self.console.configure(state="normal")
        # add a new line if there is already text
        text = self.console.get("1.0", "end-1c")
        if len(text) > 0:
            self.console.insert(tk.END, '\n')
        # log the line
        self.console.insert(tk.END, "[" + str(date.today()) + "][" + datetime.now().strftime("%H:%M:%S") + "] " + line)
        # disable the text box again
        self.console.configure(state="disabled")
        # scroll to the bottom
        self.console.yview("scroll", str(self.console.get("1.0", "end-1c").count('\n')), "units")
