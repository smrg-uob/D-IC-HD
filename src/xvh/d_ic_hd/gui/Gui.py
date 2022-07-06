from CameraElement import CameraElement
import Tkinter as tk


class Gui:
    def launch_gui(self):
        self.gui.mainloop()

    def on_press(self):
        self.camera_1.refresh_image()
        self.camera_2.refresh_image()

    def __init__(self, cameras):
        # Create the gui window
        self.gui = tk.Tk()
        self.gui.wm_title("ICHD-DIC")

        # Set full screen
        self.gui.state('zoomed')

        # sub-frame dimensions
        w_inputs = 300
        h_console = 200

        # Fetch available cameras
        self.cameras = cameras

        # Create frames for the inputs and outputs
        self.frm_input = tk.Frame(master=self.gui, width=w_inputs, relief=tk.GROOVE, borderwidth=3)
        self.frm_output = tk.Frame(master=self.gui, relief=tk.GROOVE, borderwidth=3)
        self.frm_input.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        self.frm_output.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # Prevent frame size resetting after adding widgets
        self.frm_input.pack_propagate(False)

        # For the output frame, create sub-frames for the cameras, and for the console
        self.frm_cameras = tk.Frame(master=self.frm_output)
        self.frm_console = tk.Frame(master=self.frm_output, height=h_console, relief=tk.GROOVE, borderwidth=3)
        self.frm_cameras.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.frm_console.pack(fill=tk.X, side=tk.TOP, expand=False)

        # Create the camera elements
        self.camera_1 = CameraElement(self.frm_cameras, "CAM 1", 'red', self.cameras.create_camera(0))
        self.camera_2 = CameraElement(self.frm_cameras, "CAM 2", 'blue', self.cameras.create_camera(1))

        # Add a test button to take a new image
        self.btn_1 = tk.Button(master=self.frm_input, text="Test", command=lambda: self.on_press())
        self.btn_1.pack(ipadx=5, ipady=5, expand=True)
