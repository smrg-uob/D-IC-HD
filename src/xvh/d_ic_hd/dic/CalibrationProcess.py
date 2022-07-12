import numpy as np


class CalibrationProcess:
    def __init__(self):
        self.data_sets = []

    def add_data_set(self, data_set):
        self.data_sets.append(data_set)
        return self

    def calibrate(self):
        # create parameter matrices
        theta_1 = np.zeros((3, 1))
        theta_2 = np.zeros((3, 1))
        c1 = np.zeros((3, 1))
        c2 = np.zeros((3, 1))
        d1 = np.zeros((3, 1))
        d2 = np.zeros((3, 1))
        e1 = np.zeros((3, 1))
        e2 = np.zeros((3, 1))
        # convert the data sets to matrices
        a = None
        b1 = None
        b2 = None
        for data_set in self.data_sets:
            if a is None:
                a = data_set.a
                b1 = data_set.b1
                b2 = data_set.b2
            else:
                a = np.append(a, data_set.a, 0)
                b1 = np.append(a, data_set.b1, 0)
                b2 = np.append(a, data_set.b2, 0)
