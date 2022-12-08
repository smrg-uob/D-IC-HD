# coding=utf-8

from CameraManager import CameraManager
from Tkinter import Frame
from Tkinter import SE
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngInfo
import numpy as np
from xvh.d_ic_hd.overlay import overlay
import io


# Class to display an image on a frame
class CameraFrame(Frame):
    # zoom constants
    ZOOM_VALUES = (0.5, 0.8, 1.00, 1.05, 1.10, 1.20, 1.50, 2.00, 3.00, 4.00, 5.00, 10.00)
    MAX_ZOOM = max(ZOOM_VALUES)
    MIN_ZOOM = min(ZOOM_VALUES)

    def __init__(self, tk, element, master, name, camera, logger, *pargs):
        Frame.__init__(self, master, *pargs)
        # set the element
        self.element = element
        # set the name
        self.name = name
        # set the camera
        self.camera = camera
        self.camera_manager = CameraManager(self.camera)
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
        # initialize aspect ratios
        self.ar_p = 1
        self.ar_w = 1
        self.scale_x = 1
        self.scale_y = 1
        # initialize magnification
        self.magnification = 1.0
        # initialize overlay offsets and projection
        self.ol_dx = 0.0
        self.ol_dy = 0.0
        self.ol_flip = False
        self.ol_proj = 0.0
        # take an image, copy and resize it, and convert it to a tkinter compatible image
        self.original = self.camera.grab_picture()
        self.image = Image.fromarray(self.original).resize((self.w, self.h))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.ar_p = (0.0 + self.image_width()) / (0.0 + self.image_height())
        # prevent pack propagation
        self.pack_propagate(False)
        # create the canvas for the background
        self.canvas = tk.Canvas(master=self, width=self.w, height=self.h)
        # initialize the overlay properties
        self.dpi = 200
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
        self.camera_manager = CameraManager(camera)
        self.refresh_image()

    def is_valid_camera(self):
        return self.camera.is_valid()

    def get_camera_name(self):
        return self.camera.get_name()

    def refresh_image(self):
        # tell the camera manager to grab a new picture
        if self.camera_manager.capture_image():
            # loop
            self.master.after(1, self.refresh_image_loop)

    def refresh_image_loop(self):
        if self.camera_manager.is_capturing():
            # if the camera is still capturing, loop
            self.master.after(1, self.refresh_image_loop)
        else:
            if self.camera_manager.has_captured():
                # update the image
                self.original = self.camera_manager.grab_image()
                # update aspect ratio
                self.ar_p = (0.0 + self.image_width())/(0.0 + self.image_height())
                # reset the background
                self.reset_background()
            else:
                # the camera has finished capturing, but no image was captured
                self.log('Failed to grab image, check the camera connection')

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
                self.scale_x = 1
                self.scale_y = self.ar_p / self.ar_w
            else:
                self.scale_x = self.ar_w / self.ar_p
                self.scale_y = 1
            # update the pan bounds
            self.calculate_pan_bounds()
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

    def get_zoom_index(self):
        for index, value in enumerate(CameraFrame.ZOOM_VALUES):
            if self.scale <= value:
                return index
        return len(CameraFrame.ZOOM_VALUES) - 1

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
        self.element.update_scroll_bars()

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

    def set_magnification(self, magnification):
        if magnification != self.magnification:
            self.magnification = magnification
            self.force_overlay_update()

    def set_projection(self, projection):
        if projection != self.ol_proj:
            self.ol_proj = projection
            self.force_overlay_update()

    def get_overlay_dx(self):
        return self.ol_dx

    def get_overlay_dy(self):
        return self.ol_dy

    def set_overlay_dx(self, dx):
        if dx != self.get_overlay_dx():
            self.ol_dx = dx
            self.force_overlay_update()

    def set_overlay_dy(self, dy):
        if dy != self.get_overlay_dy():
            self.ol_dy = dy
            self.force_overlay_update()

    def flip_overlay(self):
        self.ol_flip = not self.ol_flip
        self.force_overlay_update()

    def plot_overlay(self):
        self.do_overlay = True
        self.reset_background()

    def remove_overlay(self):
        self.do_overlay = False
        self.reset_background()

    def force_overlay_update(self):
        self.overlay_update = True
        if self.do_overlay:
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
                # import pyplot (do not import it at the top of the file as it would force the 'tkAgg' backend)
                import matplotlib.pyplot as plt
                # plot a new overlay
                fig = plt.figure(figsize=(self.w / self.dpi, self.h / self.dpi), dpi=self.dpi)
                ax = fig.add_subplot(111)
                ax.axis('off')
                # plot the data
                x, y, z = overlay.get_rib_1()
                self.plot_data(ax, x, y, z, "blue")
                x, y, z = overlay.get_rib_2()
                self.plot_data(ax, x, y, z, "blue")
                x, y, z = overlay.get_drill_1()
                self.plot_data(ax, x, y, z, "red")
                x, y, z = overlay.get_drill_2()
                self.plot_data(ax, x, y, z, "red")
                # get the size
                size = self.original.shape
                # configure the layout and positioning
                fig.patch.set_alpha(0)
                ax.patch.set_alpha(0)
                ax.set_position([0, 0, 1, 1])
                ax.set_xlim(-size[1]/2.0, size[1]/2.0)
                ax.set_ylim(-size[0]/2.0, size[0]/2.0)
                ax.margins(0)
                fig.set_size_inches((0.0 + size[1])/fig.get_dpi(), (0.0 + size[0])/fig.get_dpi())
                # fetch the shape of the figure
                shape = (int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1)
                # write the plot to a buffer
                io_buf = io.BytesIO()
                fig.savefig(io_buf, format='raw', dpi=fig.get_dpi())
                io_buf.seek(0)
                # convert the bytes in the buffer to a numpy array and reshape it
                self.overlay_original = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8), shape)
                # don't forget to close the buffer and the figure
                io_buf.close()
                plt.close(fig)
                # mark the update as done
                self.overlay_update = False
            # adjust for zooming and panning
            self.overlay_image = self.adjust_for_zoom_and_pan(self.overlay_original)
            # convert to a tkinter friendly image
            self.overlay = ImageTk.PhotoImage(self.overlay_image)

    def plot_data(self, ax, x, y, z, colour):
        x, y = self.rescale_overlay(x, y, z)
        ax.plot(x, y, color=colour)

    def rescale_overlay(self, x, y, z):
        # fetch field of view values
        hfov = self.camera.hfov()
        vfov = self.camera.vfov()
        # fetch magnification
        m = self.magnification
        # fetch image size
        w = self.image_width()
        h = self.image_height()
        # calculate scales
        f_x = m*(w + 0.0)/hfov
        f_y = m*(h + 0.0)/vfov
        # flip x if required
        if self.ol_flip:
            x = -x
        # project the z element away and apply the offset
        x = x + self.ol_proj*z + self.get_overlay_dx()
        y = y + self.get_overlay_dy()
        # scale the overlay from mm to pixels
        x = x*f_x
        y = y*f_y
        return x, y

    def save_image(self, file_name):
        img = Image.fromarray(self.original)
        metadata = PngInfo()
        metadata.add_text("exposure", str(self.get_exposure()))
        img.save(file_name, pnginfo=metadata)
        self.log("Saved image to " + file_name)

    def log(self, line):
        self.logger(line)
