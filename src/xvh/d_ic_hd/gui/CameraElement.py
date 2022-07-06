import Tkinter as Tk
from CameraFrame import CameraFrame


class CameraElement:
    # called when the image is scrolled horizontally
    def scrolled_x(self, type, value, unit=""):
        print("Scrolled X on " + self.name + ": " + str(value) + " " + unit + " (" + type + ")")
        pos = self.scroll_x.get()
        t_width = self.camera_frame.image_width()
        s_width = float(self.camera_frame.zoom_width())/float(t_width)
        # calculate step and delta
        step = 1.0/float(t_width)
        delta = float(value)*step
        # calculate new position
        new_mn = max(0.0, min(1.0 - s_width, pos[0] + delta))
        new_mx = new_mn + s_width
        self.scroll_x.set(new_mn, new_mx)

    # called when the image is scrolled vertically
    def scrolled_y(self, type, value, unit=""):
        print("Scrolled X on " + self.name + ": " + str(value) + " " + unit + " (" + type + ")")
        pos = self.scroll_y.get()
        t_height = self.camera_frame.image_height()
        s_height = float(self.camera_frame.zoom_height())/float(t_height)
        # calculate step and delta
        step = 1.0/float(t_height)
        delta = float(value)*step
        # calculate new position
        new_mn = max(0.0, min(1.0 - s_height, pos[0] + delta))
        new_mx = new_mn + s_height
        self.scroll_y.set(new_mn, new_mx)

    # called when the image is zoomed
    def zoom(self, type, value, unit=""):
        # fetch the current position
        pos = self.scroll_zoom.get()
        # fetch the step and delta
        step = float(CameraFrame.MIN_ZOOM)/float(CameraFrame.MAX_ZOOM)
        delta = float(value)*step
        # calculate new position
        new_mn = max(0.0, min(1.0 - step, pos[0] + delta))
        new_mx = new_mn + step
        # zoom the image
        self.camera_frame.zoom(CameraFrame.MAX_ZOOM*new_mx)
        # update the scroll bar
        self.scroll_zoom.set(new_mn, new_mx)

    def __init__(self, parent, name, camera):
        # Set the name
        self.name = name
        # Create a frame for this camera
        self.frm_main = Tk.Frame(master=parent, relief=Tk.GROOVE, borderwidth=3)
        self.frm_main.pack(fill=Tk.BOTH, side=Tk.LEFT, expand=True)
        # Prevent the frame from resetting its size
        self.frm_main.pack_propagate(False)
        # Add a label to the camera frame
        lbl = Tk.Label(master=self.frm_main, text=self.name)
        lbl.pack()
        # Create a sub-frame for the canvas with scrollbars
        frm_cvs = Tk.Frame(master=self.frm_main)
        frm_cvs.pack(fill=Tk.BOTH, side=Tk.TOP, expand=True)
        # Prevent the sub-frame from resetting its size
        frm_cvs.pack_propagate(False)
        # Configure the parent frame such that the first row and column expand freely
        frm_cvs.columnconfigure(0, weight=1, minsize=300)
        frm_cvs.rowconfigure(0, weight=1, minsize=300)
        # Create the camera frame
        self.camera_frame = CameraFrame(master=frm_cvs, camera=camera.set_exposure(10000))
        self.camera_frame.grid(row=0, column=0, sticky=(Tk.N, Tk.W, Tk.S, Tk.E))
        self.camera_frame.pack_propagate(False)
        # Create the scroll bars
        self.scroll_x = Tk.Scrollbar(master=frm_cvs, orient=Tk.HORIZONTAL, command=self.scrolled_x)
        self.scroll_y = Tk.Scrollbar(master=frm_cvs, orient=Tk.VERTICAL, command=self.scrolled_y)
        self.scroll_x.grid(row=1, column=0, sticky=(Tk.E, Tk.W))
        self.scroll_y.grid(row=0, column=1, sticky=(Tk.N, Tk.S))
        # Add controls frame
        self.frm_controls = Tk.Frame(master=self.frm_main)
        self.frm_controls.pack(fill=Tk.X, side=Tk.TOP, expand=False)
        # add zoom bar
        self.lbl_zoom = Tk.Label(master=self.frm_controls, text="Digital Zoom")
        self.scroll_zoom = Tk.Scrollbar(master=self.frm_controls, orient=Tk.HORIZONTAL, command=self.zoom)
        self.scroll_zoom.set(0, float(CameraFrame.MIN_ZOOM)/float(CameraFrame.MAX_ZOOM))
        self.lbl_zoom.grid(row=0, column=0, padx=5)
        self.scroll_zoom.grid(row=1, column=0, sticky=(Tk.E, Tk.W), padx=5)

    def refresh_image(self):
        self.camera_frame.refresh_image()
