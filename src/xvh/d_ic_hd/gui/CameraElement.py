from CameraFrame import CameraFrame
import re


class CameraElement:
    def __init__(self, tk, parent, name, camera, logger):
        # Set the parent
        self.parent = parent
        # set the logging method
        self.logger = logger
        # Set the name
        self.name = name
        # Create a frame for this camera
        self.frm_main = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_main.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        # Prevent the frame from resetting its size
        self.frm_main.pack_propagate(False)
        # Add a label to the camera frame
        lbl = tk.Label(master=self.frm_main, text=self.name)
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
        self.camera_frame = CameraFrame(tk, master=frm_cvs, camera=camera.set_exposure(10000), name=self.name, logger=logger)
        self.camera_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.S, tk.E))
        self.camera_frame.pack_propagate(False)
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
        self.frm_controls.grid_columnconfigure(0, weight=2)
        self.frm_controls.grid_columnconfigure(1, weight=10)
        self.frm_controls.grid_columnconfigure(2, weight=1)
        self.frm_controls.grid_columnconfigure(3, weight=10)
        # add zoom control
        self.lbl_zoom = tk.Label(master=self.frm_controls, text="Digital Zoom")
        self.scroll_zoom = tk.Scrollbar(master=self.frm_controls, orient=tk.HORIZONTAL, command=self.zoom)
        self.zoom_value = tk.StringVar()
        self.zoom_value.set(str(self.camera_frame.scale) + 'x')
        self.lbl_zoom_value = tk.Label(master=self.frm_controls, textvariable=self.zoom_value)
        self.scroll_zoom.set(0, float(CameraFrame.MIN_ZOOM)/float(CameraFrame.MAX_ZOOM))
        self.lbl_zoom.grid(row=0, column=0, padx=5, pady=5)
        self.scroll_zoom.grid(row=0, column=1, sticky=(tk.E, tk.W), padx=5)
        self.lbl_zoom_value.grid(row=0, column=2, sticky=(tk.E, tk.W), padx=5)
        # add exposure control
        self.lbl_exposure = tk.Label(master=self.frm_controls, text="Exposure")
        self.scroll_exposure = tk.Scrollbar(master=self.frm_controls, orient=tk.HORIZONTAL, command=self.exposure_scroll)
        exposure_validation = (self.frm_controls.register(CameraElement.validate_exposure), '%P')
        self.exposure_value = tk.StringVar()
        self.exposure_value.set(str(self.camera_frame.get_exposure()))
        self.exposure_value.trace_variable("w", self.exposure_write)
        self.ety_exposure_value = tk.Entry(master=self.frm_controls, textvariable=self.exposure_value, validate='key', validatecommand=exposure_validation)
        self.update_exposure_scroll()
        self.lbl_exposure.grid(row=1, column=0, sticky=(tk.E, tk.W), padx=5)
        self.scroll_exposure.grid(row=1, column=1, sticky=(tk.E, tk.W), padx=5)
        self.ety_exposure_value.grid(row=1, column=2, sticky=(tk.E, tk.W), padx=5)

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

    # called when the image is zoomed
    def zoom(self, type, value, unit=""):
        # get range values
        full_range = len(CameraFrame.ZOOM_VALUES)
        scroll_range = 1
        # handle the scrolling
        if CameraElement.handle_scroll(self.scroll_zoom, full_range, scroll_range, type, value, unit):
            # if scroll position has changed, update the image zoom
            self.camera_frame.set_zoom_index(len(CameraFrame.ZOOM_VALUES) * self.scroll_zoom.get()[0])
            # also update the scroll bars
            self.scrolled_x("scroll", 0)
            self.scrolled_y("scroll", 0)
            # and the scroll value
            self.zoom_value.set(str(self.camera_frame.scale) + 'x')

    # called when the exposure is changed
    def exposure_scroll(self, type, value, unit=""):
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
        pos = (int(self.exposure_value.get()) + 0.0)/(self.camera_frame.max_exposure() - self.camera_frame.min_exposure())
        self.scroll_exposure.set(pos, pos)

    def refresh_image(self):
        self.camera_frame.refresh_image()

    def log(self, line):
        self.logger(line)

    @staticmethod
    def validate_exposure(val):
        if len(val) == 0:
            return True
        return re.match('^[0-9]*$', val) is not None

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
