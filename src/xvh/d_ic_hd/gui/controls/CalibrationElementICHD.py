# coding=utf-8


class CalibrationElementICHD:
    def __init__(self, tk, parent, logger, title_font_type, title_font_size):
        # Set the parent
        self.parent = parent
        self.parent.pack_propagate(False)
        # set the logging method
        self.logger = logger
        # title
        self.lbl_cali_ichd = tk.Label(master=self.parent, text='ICHD Calibration', font=(title_font_type, title_font_size))
        self.lbl_cali_ichd.grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_ichd_todo = tk.Label(master=self.parent, text="TODO")
        self.lbl_ichd_todo.grid(row=1, column=0, sticky="w", padx=3, pady=1)

    def log(self, line):
        self.logger(line)
