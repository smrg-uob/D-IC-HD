# coding=utf-8

import tkFont
from CalibrationElementDIC import CalibrationElementDIC
from CalibrationElementICHD import CalibrationElementICHD
from DrillControlElement import DrillControlElement
from OpticsControlElement import OpticsControlElement


class ControlElement:
    def __init__(self, tk, parent, cameras, logger):
        # Set the parent
        self.parent = parent
        # set the logging method
        self.logger = logger
        # Create sub-frames
        self.frm_optics = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_cali_dic = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_cali_ichd = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_drill_control = tk.Frame(master=self.parent, relief=tk.GROOVE, borderwidth=3)
        self.frm_optics.grid(row=0, column=0, sticky="nesw")
        self.frm_drill_control.grid(row=1, column=0, sticky="nesw")
        self.frm_cali_dic.grid(row=2, column=0, sticky="nesw")
        self.frm_cali_ichd.grid(row=3, column=0, sticky="nesw")
        # Fetch default font properties
        default_font = tkFont.nametofont("TkDefaultFont")
        font_size = default_font.cget("size") + 2
        font_type = default_font.cget("family")
        # Populate optics controls
        self.optics_control = OpticsControlElement(tk, self.frm_optics, logger, cameras, font_type, font_size)
        # populate drill controls
        self.drill_control = DrillControlElement(tk, self.frm_drill_control, logger, font_type, font_size)
        # Populate DIC calibration controls
        self.dic_calibration = CalibrationElementDIC(tk, self.frm_cali_dic, logger, font_type, font_size)
        # Populate ICHD calibration controls
        self.ichd_calibration = CalibrationElementICHD(tk, self.frm_cali_ichd, logger, font_type, font_size)

    def get_magnification(self):
        return self.optics_control.get_magnification()

    def get_objective(self):
        return self.optics_control.get_objective()

    def get_projection(self):
        return self.optics_control.get_projection()

    def get_calibration(self):
        return self.ichd_calibration.get_calibration()

    def log(self, line):
        self.logger(line)

    def on_close(self):
        self.drill_control.on_close()
