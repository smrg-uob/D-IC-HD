from Tkinter import Frame
from Tkinter import Event
from Tkinter import SE
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngInfo
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from xvh.d_ic_hd.overlay import overlay

# tell matplotlib to use the tkinter backend
matplotlib.use('TkAgg')


# Class to display an image on a frame
class CameraFrame(Frame):
    # zoom constants
    ZOOM_VALUES = (1.00, 1.05, 1.10, 1.20, 1.50, 2.00, 3.00, 4.00, 5.00, 10.00)
    MAX_ZOOM = max(ZOOM_VALUES)
    MIN_ZOOM = min(ZOOM_VALUES)

    def __init__(self, tk, master, name, camera, logger, *pargs):
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
        # set the image width and height (temporarily)
        self.w = 300
        self.h = 300
        # set the zoom and pan offset
        self.scale = 1
        self.dx = 0
        self.dy = 0
        self.max_dx = 0
        self.max_dy = 0
        # take an image, copy and resize it, and convert it to a tkinter compatible image
        self.original = self.camera.grab_picture()
        self.image = Image.fromarray(self.original).resize((self.w, self.h))
        self.background_image = ImageTk.PhotoImage(self.image)
        # prevent pack propagation
        self.pack_propagate(False)
        # create the figure, axes and canvas for the image and overlay
        dpi = 254.0
        self.overlay_fig = Figure(figsize=(self.w/dpi, self.h/dpi), dpi=dpi)
        self.overlay_fig.patch.set_alpha(0)     # makes the figure background transparent
        self.overlay_axes = self.overlay_fig.add_subplot(111)
        self.overlay_axes.axis('off')
        self.overlay_axes.patch.set_alpha(0)    # makes the axes background transparent
        self.canvas = FigureCanvasTkAgg(self.overlay_fig, self)
        self.background = self.canvas.get_tk_widget()
        self.background.configure(width=self.w, height=self.h, bg='red')
        # bind the resize method to the background canvas
        self.background.bind('<Configure>', self.resize_image)
        self.background.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.canvas.draw()

    def set_camera(self, camera):
        self.camera = camera
        self.refresh_image()

    def is_valid_camera(self):
        return self.camera.is_valid()

    def get_camera_name(self):
        return self.camera.get_name()

    def refresh_image(self):
        # take a new picture
        self.original = self.camera.grab_picture()
        # reset the background
        self.reset_background()

    def resize_image(self, event):
        # fetch new width and height
        new_w = event.width
        new_h = event.height
        # update the width and height if they have changed
        if new_w != self.w or new_h != self.h:
            self.w = new_w
            self.h = new_h
            # reset the background
            self.reset_background()

    def reset_background(self):
        # resize
        copy = self.original
        if self.scale > 1:
            x1 = self.dx
            x2 = x1 + int(self.zoom_width())
            y1 = self.dy
            y2 = y1 + int(self.zoom_height())
            copy = self.original[x1:x2, y1:y2]
        self.image = Image.fromarray(copy).resize((self.w, self.h))
        # update the width and height of the canvas
        self.background.configure(width=self.w, height=self.h)
        self.background.update_idletasks()
        # create a dummy event to pass to the figure
        event = Event()
        event.width = self.w
        event.height = self.h
        self.canvas.resize(event)
        self.background.configure(scrollregion=self.background.bbox(self.background.find_all()[-1]))
        # set the new background
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.create_image(self.w, self.h, image=self.background_image, anchor=SE)
        self.canvas.draw()

    def set_zoom_index(self, index):
        scale = CameraFrame.ZOOM_VALUES[max(0, min(len(CameraFrame.ZOOM_VALUES) - 1, int(index)))]
        if scale != self.scale:
            # set the scale
            self.scale = scale
            # recalculate the panning boundaries
            self.calculate_pan_bounds()
            # update the pan position
            self.set_pan(self.dx, self.dy)

    def calculate_pan_bounds(self):
        if self.scale == 1:
            self.max_dx = 0
            self.max_dy = 0
        else:
            self.max_dx = self.image_width() - int(self.zoom_width())
            self.max_dy = self.image_height() - int(self.zoom_height())

    def set_pan_x(self, dx):
        self.set_pan(dx, self.dy)

    def set_pan_y(self, dy):
        self.set_pan(self.dx, dy)

    def set_pan(self, dx, dy):
        self.dx = max(0, min(self.max_dx, int(dx)))
        self.dy = max(0, min(self.max_dy, int(dy)))
        # reset the background
        self.reset_background()

    def image_width(self):
        return self.original.shape[0]

    def image_height(self):
        return self.original.shape[1]

    def zoom_width(self):
        return float(self.image_width())/float(self.scale)

    def zoom_height(self):
        return float(self.image_height())/float(self.scale)

    def set_exposure(self, exposure):
        self.camera.set_exposure(exposure)

    def get_exposure(self):
        return self.camera.get_exposure()

    def min_exposure(self):
        return self.camera.min_exposure()

    def max_exposure(self):
        return self.camera.max_exposure()

    def plot_overlay(self):
        x, y, z = overlay.get_rib(1000, 2)
        self.overlay_axes.plot(x, y)
        self.overlay_axes.set_position([0, 0, 1, 1])
        self.canvas.draw()

    def save_image(self, file_name):
        img = Image.fromarray(self.original)
        metadata = PngInfo()
        metadata.add_text("exposure", str(self.get_exposure()))
        img.save(file_name, pnginfo=metadata)
        self.log("Saved image to " + file_name)

    def log(self, line):
        self.logger(line)
