from CameraFrame import CameraFrame
import re
import tkFileDialog
import tkFont
import ttk
from PIL import Image, ImageTk


class CameraElement:
    def __init__(self, tk, parent, name, cameras, camera, logger):
        # Set the parent
        self.parent = parent
        # set the logging method
        self.logger = logger
        # Set the name
        self.name = name
        # Set the cameras
        self.cameras = cameras
        # Create a frame for this camera
        self.frm_main = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_main.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # Prevent the frame from resetting its size
        self.frm_main.pack_propagate(False)
        # Fetch default font properties
        default_font = tkFont.nametofont("TkDefaultFont")
        font_size = default_font.cget("size")
        font_type = default_font.cget("family")
        # Add a label to the camera frame
        lbl = tk.Label(master=self.frm_main, text=self.name, font=(font_type, font_size + 2))
        lbl.pack()
        # Create a sub-frame for the canvas with scrollbars
        frm_cvs = tk.Frame(master=self.frm_main)
        frm_cvs.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        # Prevent the sub-frame from resetting its size
        frm_cvs.pack_propagate(False)
        # Configure the parent frame such that the first row and column expand freely
        frm_cvs.columnconfigure(0, weight=1, minsize=300)
        frm_cvs.rowconfigure(0, weight=1, minsize=300)

        # Create the camera frame
        self.camera_frame = CameraFrame(tk, self, master=frm_cvs, camera=self.cameras.get_camera(camera), name=self.name, logger=logger)
        self.camera_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.S, tk.E))
        # Create the scroll bars
        self.scroll_x = tk.Scrollbar(master=frm_cvs, orient=tk.HORIZONTAL, command=self.scrolled_x)
        self.scroll_y = tk.Scrollbar(master=frm_cvs, orient=tk.VERTICAL, command=self.scrolled_y)
        self.scroll_x.grid(row=1, column=0, sticky=(tk.E, tk.W))
        self.scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scrolled_x("scroll", 0)
        self.scrolled_y("scroll", 0)

        # Add controls frame
        self.frm_controls = tk.Frame(master=self.frm_main)
        self.frm_controls.pack(fill=tk.X, side=tk.TOP, expand=False)
        for col in range(0, 120):
            self.frm_controls.grid_columnconfigure(col, weight=1)
        # add camera selection
        self.lbl_cameras = tk.Label(master=self.frm_controls, text="Camera")
        self.camera_value = tk.StringVar()
        self.camera_value.set(self.camera_frame.get_camera_name())
        self.cbx_cameras = ttk.Combobox(master=self.frm_controls, state='readonly', textvariable=self.camera_value)
        self.cbx_cameras.bind("<<ComboboxSelected>>", self.camera_selected)
        self.cbx_cameras["values"] = self.cameras.get_names()
        self.lbl_cameras.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=3, pady=1)
        self.cbx_cameras.grid(row=0, column=4, columnspan=15, sticky=(tk.W, tk.E), pady=1)
        # add capture controls
        self.lbl_capture = tk.Label(master=self.frm_controls, text="Capture")
        self.img_icon = ImageTk.PhotoImage(Image.open("resources/camera.gif"))
        self.btn_image = tk.Button(master=self.frm_controls, width=16, height=16, image=self.img_icon, command=self.button_image_pressed)
        self.btn_image.image = self.img_icon
        self.save_icon = ImageTk.PhotoImage(Image.open("resources/save.gif"))
        self.btn_save = tk.Button(master=self.frm_controls, width=16, height=16, image=self.save_icon, command=self.button_save_pressed)
        self.lbl_capture.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=3, pady=1)
        self.btn_image.grid(row=1, column=4, pady=1, sticky=tk.W)
        self.btn_save.grid(row=1, column=5, pady=1, sticky=tk.W)
        # add zoom control
        self.lbl_zoom = tk.Label(master=self.frm_controls, text="Digital Zoom")
        self.scroll_zoom = tk.Scrollbar(master=self.frm_controls, orient=tk.HORIZONTAL, command=self.zoom)
        self.zoom_value = tk.StringVar()
        self.zoom_value.set(str(self.camera_frame.scale) + 'x')
        self.lbl_zoom_value = tk.Label(master=self.frm_controls, textvariable=self.zoom_value)
        self.scroll_zoom.set(0, float(CameraFrame.MIN_ZOOM)/float(CameraFrame.MAX_ZOOM))
        self.lbl_zoom.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=3, pady=1)
        self.scroll_zoom.grid(row=2, column=4, columnspan=15, sticky=(tk.W, tk.E), pady=1)
        self.lbl_zoom_value.grid(row=2, column=19, columnspan=1, pady=1)
        # add exposure control
        self.lbl_exposure = tk.Label(master=self.frm_controls, text="Exposure")
        self.scroll_exposure = tk.Scrollbar(master=self.frm_controls, orient=tk.HORIZONTAL, command=self.exposure_scroll)
        exposure_validation = (self.frm_controls.register(CameraElement.validate_exposure), '%P')
        self.exposure_value = tk.StringVar()
        self.exposure_value.set(str(self.camera_frame.get_exposure()))
        self.exposure_value.trace_variable("w", self.exposure_write)
        self.ety_exposure = tk.Entry(master=self.frm_controls, width=9, textvariable=self.exposure_value, validate='key', validatecommand=exposure_validation)
        self.update_exposure_scroll()
        self.lbl_exposure.grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=3, pady=1)
        self.scroll_exposure.grid(row=3, column=4, columnspan=15, sticky=(tk.W, tk.E), pady=1)
        self.ety_exposure.grid(row=3, column=19, columnspan=1, pady=1)
        # add overlay toggle
        self.lbl_overlay = tk.Label(master=self.frm_controls, text="Overlay")
        self.overlay_value = tk.StringVar()
        self.overlay_value.set("Enable")
        self.btn_overlay = tk.Button(master=self.frm_controls, textvariable=self.overlay_value, command=self.button_overlay_pressed)
        self.lbl_dx = tk.Label(master=self.frm_controls, text="dx")
        float_validation = (self.frm_controls.register(CameraElement.validate_float), '%P')
        self.dx_value = tk.StringVar()
        self.dx_value.set(str(0.0))
        self.dx_value.trace_variable("w", self.dx_write)
        self.ety_dx = tk.Entry(master=self.frm_controls, width=3, textvariable=self.dx_value, validate='key', validatecommand=float_validation)
        self.lbl_dy = tk.Label(master=self.frm_controls, text="dy")
        self.dy_value = tk.StringVar()
        self.dy_value.set(str(0.0))
        self.dy_value.trace_variable("w", self.dy_write)
        self.ety_dy = tk.Entry(master=self.frm_controls, width=3, textvariable=self.dy_value, validate='key', validatecommand=float_validation)
        self.btn_flip = tk.Button(master=self.frm_controls, width=7, text="Flip", command=self.button_flip_pressed)
        self.overlay_enabled = False
        self.lbl_overlay.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=3, pady=1)
        self.btn_overlay.grid(row=4, column=4, columnspan=7, sticky=(tk.W, tk.E), pady=1)
        self.lbl_dx.grid(row=4, column=11, columnspan=1, sticky=(tk.W, tk.E), pady=1)
        self.ety_dx.grid(row=4, column=12, columnspan=3, sticky=(tk.W, tk.E), pady=1)
        self.lbl_dy.grid(row=4, column=15, columnspan=1, sticky=(tk.W, tk.E), pady=1)
        self.ety_dy.grid(row=4, column=16, columnspan=3, sticky=(tk.W, tk.E), pady=1)
        self.btn_flip.grid(row=4, column=19, sticky=tk.W, pady=1, padx=10)
        # set widget states based on camera status
        self.update_widget_states()

    # called when a camera is selected
    def camera_selected(self, event=None):
        # fetch the new camera
        camera = self.cameras.get_camera(self.cbx_cameras.current())
        # check if it is a different camera
        if camera.get_name() != self.camera_frame.get_camera_name():
            # set the camera
            self.camera_frame.set_camera(camera)
            # configure widgets
            self.update_widget_states()
            # update exposure
            self.exposure_value.set(str(camera.get_exposure()))
            self.update_exposure_scroll()
            # log
            self.log("Connected to " + camera.get_name())

    # updates the save button state
    def update_widget_states(self):
        if self.camera_frame.is_valid_camera():
            self.btn_image.configure(state="normal")
            self.btn_save.configure(state="normal")
            self.ety_exposure.configure(state="normal")
            self.btn_overlay.configure(state="normal")
            self.ety_dx.configure(state="normal")
            self.ety_dy.configure(state="normal")
        else:
            self.btn_image.configure(state="disabled")
            self.btn_save.configure(state="disabled")
            self.ety_exposure.configure(state="disabled")
            self.btn_overlay.configure(state="disabled")
            self.ety_dx.configure(state="disabled")
            self.ety_dy.configure(state="disabled")

    # called when the image button is pressed
    def button_image_pressed(self):
        self.refresh_image()

    # called when the save image button is pressed
    def button_save_pressed(self):
        fle = tkFileDialog.asksaveasfile(mode='w', defaultextension=".png")
        if fle is None:
            return
        # the file returned is opened, we need to close it first
        fle.close()
        # now pass the filename to the saving logic
        self.camera_frame.save_image(fle.name)

    # called when the overlay button is pressed
    def button_overlay_pressed(self):
        if self.overlay_enabled:
            self.overlay_value.set("Enable")
            self.camera_frame.remove_overlay()
        else:
            self.overlay_value.set("Disable")
            self.camera_frame.plot_overlay()
        self.overlay_enabled = not self.overlay_enabled

    # called when the flip button is pressed
    def button_flip_pressed(self):
        self.camera_frame.flip_overlay()

    # called when the image is scrolled horizontally
    def scrolled_x(self, type, value, unit=""):
        # get range values
        full_range = self.camera_frame.image_height()
        scroll_range = self.camera_frame.zoom_height()
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_x, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the vertical pan
            self.camera_frame.set_pan_y(full_range*self.scroll_x.get()[0])

    # called when the image is scrolled vertically
    def scrolled_y(self, type, value, unit=""):
        # get range values
        full_range = self.camera_frame.image_width()
        scroll_range = self.camera_frame.zoom_width()
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_y, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the vertical pan
            self.camera_frame.set_pan_x(full_range*self.scroll_y.get()[0])

    def update_scroll_bars(self):
        self.scrolled_x("scroll", 0)
        self.scrolled_y("scroll", 0)

    # called when the image is zoomed
    def zoom(self, type, value, unit=""):
        # check if the camera is valid
        if not self.camera_frame.is_valid_camera():
            return
        # get range values
        full_range = len(CameraFrame.ZOOM_VALUES)
        scroll_range = 1
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_zoom, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the image zoom
            self.camera_frame.set_zoom_index(len(CameraFrame.ZOOM_VALUES) * self.scroll_zoom.get()[0])
            # also update the scroll bars
            self.update_scroll_bars()
            # and the scroll value
            self.zoom_value.set(str(self.camera_frame.scale) + 'x')

    # called when the exposure is changed via the scroll bar
    def exposure_scroll(self, type, value, unit=""):
        # check if the camera is valid
        if not self.camera_frame.is_valid_camera():
            return
        # get range values
        mn = self.camera_frame.min_exposure()

        mx = self.camera_frame.max_exposure()
        rng = mx - mn
        # get current value
        current = int(self.exposure_value.get())
        exposure = current
        # handle scrolling and moving
        if type == "scroll":
            exposure = min(mx, max(mn, current + int(value)))
        if type == "moveto":
            exposure = mn + int(float(value)*rng)
        # update required
        if current != exposure:
            # update camera exposure
            self.camera_frame.set_exposure(exposure)
            # update scroll bar
            self.update_exposure_scroll()
            # update text box
            self.exposure_value.set(str(exposure))

    # called when the exposure is changed via the text box
    def exposure_write(self, *args):
        value = self.exposure_value.get()
        if len(value) == 0:
            current = 0
            exposure = self.camera_frame.min_exposure()
        else:
            current = int(value)
            exposure = max(self.camera_frame.min_exposure(), min(self.camera_frame.max_exposure(), current))
        if current != exposure:
            # update text box value
            self.exposure_value.set(str(exposure))
        # update scroll bar
        self.update_exposure_scroll()
        # update camera exposure
        self.camera_frame.set_exposure(exposure)

    def update_exposure_scroll(self):
        if self.camera_frame.max_exposure() == 0 or self.camera_frame.max_exposure() == self.camera_frame.min_exposure():
            pos = 0
        else:
            pos = (int(self.exposure_value.get()) + 0.0)/(self.camera_frame.max_exposure() - self.camera_frame.min_exposure())
        self.scroll_exposure.set(pos, pos)

    def refresh_image(self):
        self.camera_frame.refresh_image()

    def dx_write(self, *args):
        val = self.ety_dx.get()
        if len(val) == 0 or val == '-':
            dx = 0
        else:
            dx = float(val)
        self.camera_frame.set_overlay_dx(dx)

    def dy_write(self, *args):
        val = self.ety_dy.get()
        if len(val) == 0 or val == '-':
            dy = 0
        else:
            dy = float(val)
        self.camera_frame.set_overlay_dy(dy)

    def update_magnification(self, magnification):
        self.camera_frame.set_magnification(magnification)

    def update_projection(self, projection):
        self.camera_frame.set_projection(projection)

    def log(self, line):
        self.logger(self.name + ": " + line)

    @staticmethod
    def validate_exposure(val):
        if len(val) == 0:
            return True
        return re.match('^[0-9]*$', val) is not None

    @staticmethod
    def validate_float(val):
        if len(val) == 0 or val == '-':
            return True
        try:
            float(val)
        except:
            return False
        return True

    @staticmethod
    def handle_scroll(scroll_bar, full_range, scroll_range, type, value, unit=""):
        current = scroll_bar.get()
        old_mn = current[0]*full_range
        old_mx = current[1]*full_range
        new_mn = old_mn
        new_mx = old_mx
        if type == "scroll":
            new_mn = max(0.0, min(full_range - scroll_range + 0.0, new_mn + float(value)))/full_range
            new_mx = new_mn + scroll_range/(0.0 + full_range)
        if type == "moveto":
            new_mn = max(0.0, min(full_range - scroll_range + 0.0, float(value)*full_range))/full_range
            new_mx = new_mn + scroll_range/(0.0 + full_range)
        if new_mn != old_mn or new_mx != old_mx:
            scroll_bar.set(new_mn, new_mx)
            return True
        return False
