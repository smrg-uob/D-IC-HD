from xvh.d_ic_hd.util import input_validation


class OpticsControlElement:
    def __init__(self, tk, parent, logger, cameras, title_font_type, title_font_size):
        # Set the parent
        self.parent = parent
        # Set the cameras
        self.cameras = cameras
        # set the logging method
        self.logger = logger
        self.lbl_optics = tk.Label(self.parent, text='Optics', font=(title_font_type, title_font_size))
        self.lbl_optics.grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_magnification = tk.Label(self.parent, text="Magnification")
        magnification_validation = (parent.register(input_validation.validate_float_positive), '%P')
        self.magnification_value = tk.StringVar()
        self.magnification_value.set(str(2.4))
        self.magnification_value.trace_variable("w", self.magnification_write)
        self.ety_magnification = tk.Entry(self.parent, width=9, textvariable=self.magnification_value,
                                          validate='key', validatecommand=magnification_validation)
        self.lbl_magnification.grid(row=1, column=0, sticky="w", padx=3, pady=1)
        self.ety_magnification.grid(row=1, column=1, sticky="e", pady=1)
        self.lbl_objective = tk.Label(self.parent, text="Objective")
        self.objective_value = tk.StringVar()
        self.objective_value.set(str(0.3))
        self.objective_value.trace_variable("w", self.objective_write)
        self.ety_objective = tk.Entry(self.parent, width=9, textvariable=self.objective_value,
                                      validate='key', validatecommand=magnification_validation)
        self.lbl_objective.grid(row=2, column=0, sticky="w", padx=3, pady=1)
        self.ety_objective.grid(row=2, column=1, sticky="e", pady=1)
        self.lbl_projection = tk.Label(self.parent, text="Projection")
        projection_validation = (parent.register(input_validation.validate_float), '%P')
        self.projection_value = tk.StringVar()
        self.projection_value.set(str(0.0))
        self.projection_value.trace_variable("w", self.projection_write)
        self.ety_projection = tk.Entry(self.parent, width=9, textvariable=self.projection_value,
                                          validate='key', validatecommand=projection_validation)
        self.lbl_projection.grid(row=3, column=0, sticky="w", padx=3, pady=1)
        self.ety_projection.grid(row=3, column=1, sticky="e", pady=1)
        # Notify the cameras of the default magnification
        self.update_magnification()

    def magnification_write(self, *args):
        self.update_magnification()

    def objective_write(self, *args):
        self.update_magnification()

    def projection_write(self, *args):
        projection = self.get_projection()
        for camera in self.cameras:
            camera.update_projection(projection)

    def update_magnification(self):
        magnification = self.get_magnification()*self.get_objective()
        for camera in self.cameras:
            camera.update_magnification(magnification)

    def get_magnification(self):
        val = self.magnification_value.get()
        if len(val) == 0:
            return 1.0
        return float(val)

    def get_objective(self):
        val = self.objective_value.get()
        if len(val) == 0:
            return 1.0
        return float(val)

    def get_projection(self):
        val = self.projection_value.get()
        if len(val) == 0 or val == '-':
            return 0.0
        return float(val)

    def log(self, line):
        self.logger(line)