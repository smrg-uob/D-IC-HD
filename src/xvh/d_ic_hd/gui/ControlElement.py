import tkFont
from DrillControlElement import DrillControlElement
from xvh.d_ic_hd.util import input_validation


class ControlElement:
    def __init__(self, tk, parent, cameras, logger):
        # Set the parent
        self.parent = parent
        # Set the cameras
        self.cameras = cameras
        # set the logging method
        self.logger = logger
        # Create sub-frames
        self.frm_optics = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_cali_dic = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_cali_ichd = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_drill_control = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_optics.grid(row=0, column=0, sticky="nesw")
        self.frm_cali_dic.grid(row=1, column=0, sticky="nesw")
        self.frm_cali_ichd.grid(row=2, column=0, sticky="nesw")
        self.frm_drill_control.grid(row=3, column=0, sticky="nesw")
        # Fetch default font properties
        default_font = tkFont.nametofont("TkDefaultFont")
        font_size = default_font.cget("size") + 2
        font_type = default_font.cget("family")
        # Populate optics controls
        self.lbl_optics = tk.Label(master=self.frm_optics, text='Optics', font=(font_type, font_size))
        self.lbl_optics.grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_magnification = tk.Label(master=self.frm_optics, text="Magnification")
        magnification_validation = (self.frm_optics.register(input_validation.validate_float_positive), '%P')
        self.magnification_value = tk.StringVar()
        self.magnification_value.set(str(2.4))
        self.magnification_value.trace_variable("w", self.magnification_write)
        self.ety_magnification = tk.Entry(master=self.frm_optics, width=9, textvariable=self.magnification_value,
                                          validate='key', validatecommand=magnification_validation)
        self.lbl_magnification.grid(row=1, column=0, sticky="w", padx=3, pady=1)
        self.ety_magnification.grid(row=1, column=1, sticky="e", pady=1)
        self.lbl_objective = tk.Label(master=self.frm_optics, text="Objective")
        self.objective_value = tk.StringVar()
        self.objective_value.set(str(0.3))
        self.objective_value.trace_variable("w", self.objective_write)
        self.ety_objective = tk.Entry(master=self.frm_optics, width=9, textvariable=self.objective_value,
                                      validate='key', validatecommand=magnification_validation)
        self.lbl_objective.grid(row=2, column=0, sticky="w", padx=3, pady=1)
        self.ety_objective.grid(row=2, column=1, sticky="e", pady=1)
        self.lbl_projection = tk.Label(master=self.frm_optics, text="Projection")
        projection_validation = (self.frm_optics.register(input_validation.validate_float), '%P')
        self.projection_value = tk.StringVar()
        self.projection_value.set(str(0.0))
        self.projection_value.trace_variable("w", self.projection_write)
        self.ety_projection = tk.Entry(master=self.frm_optics, width=9, textvariable=self.projection_value,
                                          validate='key', validatecommand=projection_validation)
        self.lbl_projection.grid(row=3, column=0, sticky="w", padx=3, pady=1)
        self.ety_projection.grid(row=3, column=1, sticky="e", pady=1)
        # Populate DIC calibration controls
        self.lbl_cali_dic = tk.Label(master=self.frm_cali_dic, text='DIC Calibration', font=(font_type, font_size))
        self.lbl_cali_dic.grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_dic_todo = tk.Label(master=self.frm_cali_dic, text="TODO")
        self.lbl_dic_todo.grid(row=1, column=0, sticky="w", padx=3, pady=1)
        # Populate ICHD calibration controls
        self.lbl_cali_ichd = tk.Label(master=self.frm_cali_ichd, text='ICHD Calibration', font=(font_type, font_size))
        self.lbl_cali_ichd.grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_ichd_todo = tk.Label(master=self.frm_cali_ichd, text="TODO")
        self.lbl_ichd_todo.grid(row=1, column=0, sticky="w", padx=3, pady=1)
        # populate drill controls
        self.drill_control = DrillControlElement(tk, self.frm_drill_control, logger, font_type, font_size)
        # Notify the cameras of the default magnification
        self.update_magnification()

    def magnification_write(self, *args):
        self.update_magnification()

    def objective_write(self, *args):
        self.update_magnification()

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

    def update_magnification(self):
        magnification = self.get_magnification()*self.get_objective()
        for camera in self.cameras:
            camera.update_magnification(magnification)

    def projection_write(self, *args):
        projection = self.get_projection()
        for camera in self.cameras:
            camera.update_projection(projection)

    def get_projection(self):
        val = self.projection_value.get()
        if len(val) == 0 or val == '-':
            return 0.0
        return float(val)

    def log(self, line):
        self.logger(line)

    def on_close(self):
        self.drill_control.on_close()
