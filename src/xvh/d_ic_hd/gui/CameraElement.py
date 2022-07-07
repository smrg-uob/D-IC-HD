import Tkinter as Tk
from CameraFrame import CameraFrame


class CameraElement:
    # called when the image is scrolled horizontally
    def scrolled_x(self, type, value, unit=""):
        # get range values
        full_range = self.camera_frame.image_width()
        scroll_range = self.camera_frame.zoom_width()
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_x, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the vertical pan
            self.camera_frame.set_pan_x(full_range*self.scroll_x.get()[0])

    # called when the image is scrolled vertically
    def scrolled_y(self, type, value, unit=""):
        # get range values
        full_range = self.camera_frame.image_height()
        scroll_range = self.camera_frame.zoom_height()
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_y, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the vertical pan
            self.camera_frame.set_pan_y(full_range*self.scroll_y.get()[0])

    # called when the image is zoomed
    def zoom(self, type, value, unit=""):
        # get range values
        full_range = CameraFrame.MAX_ZOOM
        scroll_range = CameraFrame.MIN_ZOOM
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_zoom, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the image zoom
            self.camera_frame.zoom(CameraFrame.MAX_ZOOM*self.scroll_zoom.get()[1])

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

    @staticmethod
    def handle_scroll(scroll_bar, full_range, scroll_range, type, value, unit=""):
        current = scroll_bar.get()
        old_mn = current[0]*full_range
        old_mx = current[1]*full_range
        new_mn = old_mn
        new_mx = old_mx
        if type == "scroll":
            new_mn = max(0.0, min(full_range - scroll_range, new_mn + float(value)))/full_range
            new_mx = new_mn + scroll_range/full_range
        if type == "moveto":
            new_mn = max(0.0, min(full_range - scroll_range, float(value)*full_range))/full_range
            new_mx = new_mn + scroll_range/full_range
        if new_mn != old_mn or new_mx != old_mx:
            scroll_bar.set(new_mn, new_mx)
            return True
        return False
