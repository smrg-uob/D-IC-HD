import Tkinter as Tk
from Tkinter import Frame
from Tkinter import Label
from PIL import Image, ImageTk


# Class to display an image on a frame
class CameraFrame(Frame):
    # zoom constants
    MIN_ZOOM = 1
    MAX_ZOOM = 20

    def __init__(self, master, name, camera, logger, *pargs):
        Frame.__init__(self, master, *pargs)
        # set the name
        self.name = name
        # set the camera
        self.camera = camera
        # set the logging method
        self.logger = logger
        # check if the camera is valid
        if self.camera.is_valid():
            self.log(self.name + ": Connected to " + self.camera.get_name())
        else:
            self.log(self.name + ": Invalid camera requested")
        # set the width and height (temporarily)
        self.w = 300
        self.h = 300
        # set the zoom and pan offset
        self.scale = 1
        self.dx = 0
        self.dy = 0
        self.max_dx = 0
        self.max_dy = 0
        # take an image, and copy and resize it
        self.original = Image.fromarray(self.camera.grab_picture())
        self.image = self.original.copy().resize((self.w, self.h))
        # set the background image and bind the resize method to it
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=Tk.BOTH, expand=Tk.YES)
        self.background.bind('<Configure>', self.resize_image)

    def refresh_image(self):
        # take a new picture
        self.original = Image.fromarray(self.camera.grab_picture())
        # reset the background
        self.reset_background()

    def resize_image(self, event):
        # fetch new width and height
        self.w = event.width
        self.h = event.height
        # reset the background
        self.reset_background()

    def reset_background(self):
        # resize
        self.image = self.original.copy().resize((self.w, self.h))
        # set the new background
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)

    def zoom(self, scale):
        new_scale = max(CameraFrame.MIN_ZOOM, min(CameraFrame.MIN_ZOOM, int(scale)))
        if new_scale != self.scale:
            # set the scale
            self.scale = new_scale
            # recalculate the panning boundaries
            self.calculate_pan_bounds()
            # update the pan position
            self.set_pan(self.dx, self.dy)

    def calculate_pan_bounds(self):
        if self.scale == 1:
            self.max_dx = 0
            self.max_dy = 0
        else:
            self.max_dx = self.image_width() - self.zoom_width()
            self.max_dy = self.image_height() - self.zoom_height()

    def set_pan_x(self, dx):
        self.set_pan(dx, self.dy)

    def set_pan_y(self, dy):
        self.set_pan(self.dx, dy)

    def set_pan(self, dx, dy):
        self.dx = max(0, min(self.max_dx, dx))
        self.dy = max(0, min(self.max_dy, dy))
        # reset the background
        # TODO

    def image_width(self):
        return self.original.size[0]

    def image_height(self):
        return self.original.size[0]

    def zoom_width(self):
        return float(self.image_width())/float(self.scale)

    def zoom_height(self):
        return float(self.image_height())/float(self.scale)

    def log(self, line):
        self.logger(line)
