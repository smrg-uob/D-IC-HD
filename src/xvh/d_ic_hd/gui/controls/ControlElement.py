import tkFont
from xvh.d_ic_hd.gui.controls.DrillControlElement import DrillControlElement
from xvh.d_ic_hd.gui.controls.OpticsControlElement import OpticsControlElement


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
        self.frm_cali_dic.grid(row=1, column=0, sticky="nesw")
        self.frm_cali_ichd.grid(row=2, column=0, sticky="nesw")
        self.frm_drill_control.grid(row=3, column=0, sticky="nesw")
        # Fetch default font properties
        default_font = tkFont.nametofont("TkDefaultFont")
        font_size = default_font.cget("size") + 2
        font_type = default_font.cget("family")
        # Populate optics controls
        self.optics_control = OpticsControlElement(tk, self.frm_optics, logger, cameras, font_type, font_size)
        # populate drill controls
        self.drill_control = DrillControlElement(tk, self.frm_drill_control, logger, font_type, font_size)
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

    def get_magnification(self):
        return self.optics_control.get_magnification()

    def get_objective(self):
        return self.optics_control.get_objective()

    def get_projection(self):
        return self.optics_control.get_projection()

    def log(self, line):
        self.logger(line)

    def on_close(self):
        self.drill_control.on_close()
