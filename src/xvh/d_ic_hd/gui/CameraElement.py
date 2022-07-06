import Tkinter as Tk
from CameraFrame import CameraFrame


class CameraElement:
    def scrolled_x(self, type, value, unit=""):
        print("Scrolled X on " + self.name + ": " + str(value) + " " + unit + " (" + type + ")")
        pos = self.scroll_x.get()
        width = 100
        nr = float(value)
        if unit == "":
            new_mn = min(nr, (width - 1)/width)
            new_mx = new_mn + 1/width
        else:
            new_mn = max(0, min(pos[0]*width + nr, width - 1))/width
            new_mx = max(new_mn*width + 1, min(pos[1]*width + nr, width))/width
        self.scroll_x.set(new_mn, new_mx)

    def scrolled_y(self, type, value, unit=""):
        print("Scrolled Y on " + self.name + ": " + str(value) + " " + unit + " (" + type + ")")

    def __init__(self, parent, name, colour, camera):
        # Set the name
        self.name = name
        # Create a frame for this camera
        self.frame = Tk.Frame(master=parent, relief=Tk.GROOVE, borderwidth=3)
        self.frame.pack(fill=Tk.BOTH, side=Tk.LEFT, expand=True)
        # Prevent the frame from resetting its size
        self.frame.pack_propagate(False)
        # Add a label to the camera frame
        lbl = Tk.Label(master=self.frame, text=self.name)
        lbl.pack()
        # Create a sub-frame for the canvas with scrollbars
        frm_cvs = Tk.Frame(master=self.frame)
        frm_cvs.pack(fill=Tk.BOTH, side=Tk.TOP, expand=True)
        # Prevent the sub-frame from resetting its size
        frm_cvs.pack_propagate(False)
        # Configure the parent frame such that the first row and column expand freely
        frm_cvs.columnconfigure(0, weight=1, minsize=300)
        frm_cvs.rowconfigure(0, weight=1, minsize=300)
        # Create the camera frame
        self.camera_frame = CameraFrame(master=frm_cvs, camera=camera.set_exposure(10000))
        self.camera_frame.grid(row=0, column=0, sticky=(Tk.N, Tk.W, Tk.S, Tk.E))
        # Create the scroll bars
        self.scroll_x = Tk.Scrollbar(master=frm_cvs, orient=Tk.HORIZONTAL, command=self.scrolled_x)
        self.scroll_y = Tk.Scrollbar(master=frm_cvs, orient=Tk.VERTICAL, command=self.scrolled_y)
        self.scroll_x.grid(row=1, column=0, sticky=(Tk.E, Tk.W))
        self.scroll_y.grid(row=0, column=1, sticky=(Tk.N, Tk.S))

    def refresh_image(self):
        self.camera_frame.refresh_image()
