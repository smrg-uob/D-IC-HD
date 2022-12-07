# coding=utf-8

import os
import tkFileDialog
import ttk
from xvh.d_ic_hd.ichd import ICHD_Calibration
from xvh.d_ic_hd.util import input_validation

class CalibrationElementICHD:
    def __init__(self, tk, parent, logger, title_font_type, title_font_size):
        # Set the parent
        self.parent = parent
        self.parent.pack_propagate(False)
        # calibration data
        self.calibrator = None
        self.calibration = None
        # set the logging method
        self.logger = logger
        # title
        self.lbl_cali_ichd = tk.Label(master=self.parent, text='ICHD Calibration', font=(title_font_type, title_font_size))
        self.lbl_cali_ichd.grid(row=0, column=0, sticky="w", pady=2)
        # Add controls frame
        self.frm_controls = tk.Frame(master=self.parent)
        self.frm_controls.grid(row=1, column=0, sticky="nesw",)
        # column configuration
        row = 0
        span_1 = 7
        span_2 = 24
        span_3 = 6
        span_full = span_1 + span_2 + span_3
        col_1 = 0
        col_2 = col_1 + span_1
        col_3 = col_2 + span_2
        for col in range(0, col_3 + span_3):
            self.frm_controls.grid_columnconfigure(col, weight=1)
        # load directory widgets
        self.lbl_directory = tk.Label(master=self.frm_controls, text='Directory')
        self.directory_value = tk.StringVar()
        self.directory_value.set('')
        self.directory_value.trace_variable("w", self.on_directory_changed)
        self.ety_directory = tk.Entry(master=self.frm_controls, width=span_1 + span_2, textvariable=self.directory_value)
        self.browse_value = tk.StringVar()
        self.browse_value.set('Browse')
        self.btn_browse_directory = tk.Button(master=self.frm_controls, textvariable=self.browse_value, command=self.browse_directory_button_pressed)
        self.lbl_directory.grid(row=row, column=col_1, columnspan=span_full, sticky=tk.W, padx=3, pady=1)
        self.ety_directory.grid(row=row + 1, column=col_1, columnspan=span_1 + span_2, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_browse_directory.grid(row=row + 1, column=col_3, columnspan=span_3, sticky=(tk.W, tk.E), padx=3, pady=1)
        row = row + 2
        # calibration widgets
        self.lbl_increments = tk.Label(master=self.frm_controls, text='Increments')
        validation = (self.frm_controls.register(input_validation.validate_int_positive), '%P')
        self.increments_value = tk.StringVar()
        self.increments_value.set('1')
        self.ety_increments = tk.Entry(master=self.frm_controls, width=4, textvariable=self.increments_value, validate='key', validatecommand=validation)
        self.pb_calibration = ttk.Progressbar(master=self.frm_controls, orient=tk.HORIZONTAL, length=span_2 - 4, mode='determinate')
        self.calibrate_value = tk.StringVar()
        self.calibrate_value.set('Calibrate')
        self.btn_calibrate = tk.Button(master=self.frm_controls, textvariable=self.calibrate_value, command=self.on_calibrate_button_pressed)
        self.lbl_increments.grid(row=row, column=col_1, columnspan=span_1, sticky=tk.W, padx=3, pady=1)
        self.ety_increments.grid(row=row, column=col_2, columnspan=4, sticky=None, padx=3, pady=1)
        self.pb_calibration.grid(row=row, column=col_2 + 4, columnspan=span_2 - 4, sticky=(tk.W, tk.E), padx=3, pady=1)
        self.btn_calibrate.grid(row=row, column=col_3, columnspan=span_3, sticky=(tk.W, tk.E), padx=3, pady=1)
        # update widget states
        self.update_widget_states()

    # calibration progress loop
    def calibration_progress_loop(self):
        if self.calibrator is None:
            if self.calibration is None:
                # reset the progress
                self.pb_calibration.configure(value=0)
                self.pb_calibration.configure(maximum=1)
            else:
                # set the progress to full
                self.pb_calibration.configure(value=1)
                self.pb_calibration.configure(maximum=1)
            # update widgets
            self.update_widget_states()
        else:
            # update the progress bar
            progress, total = self.calibrator.get_progress()
            self.pb_calibration.configure(value=progress)
            self.pb_calibration.configure(maximum=total)
            # loop
            self.parent.after(1, self.calibration_progress_loop)

    # called when the open calibration folder button is pressed
    def browse_directory_button_pressed(self):
        fle = tkFileDialog.askdirectory()
        if fle is None:
            return
        self.directory_value.set(fle)

    # called when the calibrate button is pressed
    def on_calibrate_button_pressed(self):
        if self.calibration is None:
            if self.calibrator is None:
                # launch calibration
                if self.calibrate():
                    # start progress loop
                    self.calibration_progress_loop()
            else:
                # Stop the calibrator
                self.calibrator.stop()
        else:
            # clear calibration
            self.calibration = None
            # clear calibration progress
            self.pb_calibration.configure(value=0)
            self.pb_calibration.configure(maximum=1)
            # log message
            self.log('Calibration Reset')
        # update widget states
        self.update_widget_states()

    # called when the directory field is written to
    def on_directory_changed(self, *args):
        self.update_widget_states()

    # run calibration
    def calibrate(self):
        # Check if the increments are defined
        increment_string = self.increments_value.get()
        if increment_string is None or len(increment_string) <= 0:
            self.log('Calibration failed: a calibration must be for at least 1 increment')
            return False
        # Check if the increments value is larger than 0
        increments = int(increment_string)
        if increments <= 0:
            self.log('Calibration failed: a calibration must be for at least 1 increment')
            return False
        # check if the directory is valid
        directory = self.get_calibration_dir()
        if not os.path.isdir(directory):
            self.log('Calibration failed: invalid directory')
            return False
        # request a calibration
        self.calibrator = ICHD_Calibration.request_calibration(self.calibration_callback, increments, directory)
        # success
        return True

    # callback for accepting calibrations
    def calibration_callback(self, calibration, feedback):
        # remove the calibrator
        self.calibrator = None
        # check if calibration was successful
        if calibration is None:
            # log a message
            self.log('Calibration failed: ' + feedback)
        else:
            # log a message
            self.log(feedback)
            # store the calibration
            self.calibration = calibration
        # update widgets
        self.update_widget_states()

    # fetches the current calibration directory
    def get_calibration_dir(self):
        return self.directory_value.get()

    # updates widget states
    def update_widget_states(self):
        if self.calibration is None:
            if self.calibrator is None:
                # configure calibration button
                self.btn_calibrate.configure(state='normal')
                self.calibrate_value.set('Calibrate')
                # configure directory
                self.btn_browse_directory.configure(state='normal')
                self.ety_directory.configure(state='normal')
                # configure incrementation
                directory = self.get_calibration_dir()
                if directory is None or directory == '':
                    self.ety_increments.configure(state='disabled')
                    self.btn_calibrate.configure(state='disabled')
                else:
                    self.ety_increments.configure(state='normal')
                    self.btn_calibrate.configure(state='normal')
            else:
                # configure calibration button
                self.btn_calibrate.configure(state='normal')
                self.calibrate_value.set('Abort')
                if self.calibrator.is_stopped():
                    self.btn_calibrate.configure(state='disabled')
                # disable all other widgets
                self.ety_directory.configure(state='disabled')
                self.btn_browse_directory.configure(state='disabled')
                self.ety_increments.configure(state='disabled')
        else:
            # configure calibration button
            self.btn_calibrate.configure(state='normal')
            self.calibrate_value.set('Reset')
            # configure all other widgets
            self.btn_browse_directory.configure(state='normal')
            self.ety_directory.configure(state='disabled')
            self.ety_increments.configure(state='disabled')

    def log(self, line):
        self.logger('ICHD Calibration: ' + line)

    def on_close(self):
        if self.calibrator is not None:
            self.calibrator.stop()
            self.calibrator = None
