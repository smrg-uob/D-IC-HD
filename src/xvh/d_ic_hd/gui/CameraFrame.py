from Tkinter import Frame
from Tkinter import SE
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngInfo
import numpy as np
import matplotlib.pyplot as plt
from xvh.d_ic_hd.overlay import overlay
import io


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
        self.ar_p = 1
        self.ar_w = 1
        self.scale_x = 1
        self.scale_y = 1
        # take an image, copy and resize it, and convert it to a tkinter compatible image
        self.original = self.camera.grab_picture()
        self.image = Image.fromarray(self.original).resize((self.w, self.h))
        self.background_image = ImageTk.PhotoImage(self.image)
        # prevent pack propagation
        self.pack_propagate(False)
        # create the canvas for the background
        self.canvas = tk.Canvas(master=self, width=self.w, height=self.h)
        # create the figure and axes for the overlay
        dpi = 100
        self.ol_fig = plt.figure(figsize=(self.w / dpi, self.h / dpi), dpi=dpi)
        self.ol_fig.patch.set_alpha(0)
        self.ol_axes = self.ol_fig.add_subplot(111)
        self.ol_axes.axis('off')
        self.ol_axes.patch.set_alpha(0)
        self.overlay_update = True
        self.do_overlay = False
        self.overlay_original = None
        self.overlay_image = None
        self.overlay = None
        # bind the resize method to the background canvas
        self.canvas.bind('<Configure>', self.resize_image)
        self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

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
        # update aspect ratio
        self.ar_p = (0.0 + self.image_width())/(0.0 + self.image_height())
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
            # update the aspect ratio
            self.ar_w = (0.0 + self.w)/(0.0 + self.h)
            # update the ar scale
            if self.ar_w == self.ar_p:
                self.scale_x = 1
                self.scale_y = 1
            elif self.ar_w < self.ar_p:
                self.scale_x = self.ar_p / self.ar_w
                self.scale_y = 1
            else:
                self.scale_x = 1
                self.scale_y = self.ar_w / self.ar_p
            # reset the background
            self.reset_background()

    def reset_background(self):
        # adjust for zooming and panning
        self.image = self.adjust_for_zoom_and_pan(self.original)
        # update the width and height of the canvas
        self.canvas.configure(width=self.w, height=self.h)
        # set the new background
        self.background_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(self.w, self.h, image=self.background_image, anchor=SE)
        if self.do_overlay:
            self.refresh_overlay()
            self.canvas.create_image(self.w, self.h, image=self.overlay, anchor=SE)

    def adjust_for_zoom_and_pan(self, array):
        x1 = self.dx
        x2 = x1 + int(self.zoom_width())
        y1 = self.dy
        y2 = y1 + int(self.zoom_height())
        copy = array[x1:x2, y1:y2]
        return Image.fromarray(copy).resize((self.w, self.h))

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
        return float(self.image_width())/float(self.scale*self.scale_x)

    def zoom_height(self):
        return float(self.image_height())/float(self.scale*self.scale_y)

    def set_exposure(self, exposure):
        self.camera.set_exposure(exposure)

    def get_exposure(self):
        return self.camera.get_exposure()

    def min_exposure(self):
        return self.camera.min_exposure()

    def max_exposure(self):
        return self.camera.max_exposure()

    def plot_overlay(self):
        self.do_overlay = True
        self.reset_background()

    def remove_overlay(self):
        self.do_overlay = False
        self.reset_background()

    def refresh_overlay(self):
        # we save the overlay plot to a PIL image and draw it on the canvas afterwards
        # the alternatives are:
        # - create a matplotlib tkinter canvas onto which we can plot directly and set its background as normal
        # - create a matplotlib tkinter canvas on top of the background canvas
        # the issues with these are:
        # - the first approach causes the plot to appear behind the image, and has a huge hit on performance
        # - for the second approach, it is not easily feasible to make the overlay canvas background transparent
        if self.do_overlay:
            if self.overlay_update:
                # clear the previous plot
                self.ol_axes.clear()
                # plot the data
                x, y, z = overlay.get_rib(1000, 2)
                x, y = self.rescale(x, y)
                self.ol_axes.plot(x, y)
                # get the size
                size = self.original.shape
                # reset the positioning
                self.ol_axes.patch.set_alpha(0)
                self.ol_axes.set_position([0, 0, 1, 1])
                self.ol_axes.set_xlim(0, size[1])
                self.ol_axes.set_xlim(0, size[0])
                self.ol_axes.margins(0)
                self.ol_fig.set_size_inches((0.0 + size[1])/self.ol_fig.get_dpi(), (0.0 + size[0])/self.ol_fig.get_dpi())
                # fetch the shape of the figure
                shape = (int(self.ol_fig.bbox.bounds[3]), int(self.ol_fig.bbox.bounds[2]), -1)
                # write the plot to a buffer
                io_buf = io.BytesIO()
                self.ol_fig.savefig(io_buf, format='raw', dpi=self.ol_fig.get_dpi())
                io_buf.seek(0)
                # convert the bytes in the buffer to a numpy array and reshape it
                self.overlay_original = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8), shape)
                # don't forget to close the buffer
                io_buf.close()
                # mark the update as done
                self.overlay_update = False
            # adjust for zooming and panning
            self.overlay_image = self.adjust_for_zoom_and_pan(self.overlay_original)
            # convert to a tkinter friendly image
            self.overlay = ImageTk.PhotoImage(self.overlay_image)

    def rescale(self, x, y):
        # TODO: define magnification factor from the optics
        x = (x/max(x))*self.w
        y = (y/max(y))*self.h
        return x, y

    def save_image(self, file_name):
        img = Image.fromarray(self.original)
        metadata = PngInfo()
        metadata.add_text("exposure", str(self.get_exposure()))
        img.save(file_name, pnginfo=metadata)
        self.log("Saved image to " + file_name)

    def log(self, line):
        self.logger(line)
