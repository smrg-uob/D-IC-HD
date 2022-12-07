# coding=utf-8

import numpy as np
import openpyxl
import os
import threading


class ICHD_Calibration:
    def __init__(self):
        pass


class Calibrator:

    def __init__(self, callback, increments, directory):
        self.callback = callback
        self.increments = increments
        self.directory = directory
        self.progress = 0
        self.total = (self.increments*(self.increments + 1))/2
        self.stop_calibration = False
        self.calibration_thread = threading.Thread(target=self.__calibrate)
        self.calibration_thread.start()

    def __calibrate(self):
        for depth in np.arange(1, self.increments + 1):
            for increment in np.arange(1, depth + 1):
                # stop check
                if self.is_stopped():
                    self.callback(None, 'Calibration interrupted')
                    return
                # treat the next Excel file
                file_name = 'Out_Depth_' + str(depth) + '_Inc_' + str(increment) + '.xlsx'
                file_path = self.directory + '/' + file_name
                # check that the file exists
                if not os.path.exists(file_path):
                    # If the excel file does not exist, stop
                    self.callback(None, 'File ' + file_name + ' not found in directory')
                    return
                # load the excel file
                excel_file = openpyxl.load_workbook(file_path)
                # TODO
                # close the excel file again
                excel_file.close()
                # update progress
                self.progress = self.progress + 1
        self.callback('TODO', 'Calibration complete')   # TODO

    def get_progress(self):
        return self.progress, self.total

    def stop(self):
        self.stop_calibration = True
        # TODO: check if we can kill the thread somehow...

    def is_stopped(self):
        return self.stop_calibration


def request_calibration(callback, increments, directory):
    return Calibrator(callback, increments, directory)
