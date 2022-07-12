import numpy as np


class Calibration:
    def __init__(self):
        # camera 1 orientation
        self.theta_1 = np.asarray((0, 0, 0))
        # camera 1 pinhole position
        self.c_1 = np.asarray((0, 0, 0))
        # camera 1 projection vector
        self.d_1 = np.asarray((0, 0, 0))
        # camera 1 detector plate position
        self.e_1 = np.asarray((0, 0, 0))
        # camera 2 orientation
        self.theta_2 = np.asarray((0, 0, 0))
        # camera 2 pinhole position
        self.c_2 = np.asarray((0, 0, 0))
        # camera 2 projection vector
        self.d_2 = np.asarray((0, 0, 0))
        # camera 2 detector plate position
        self.e_2 = np.asarray((0, 0, 0))
