import numpy as np


class CalibrationDataSet:

    def __init__(self, a, b1, b2):
        # Coordinates of the points in 3D space (in mm)
        self.a = a
        # Coordinates of the points on the first camera (in pixels)
        self.b1 = b1
        # Coordinates of the points on the second camera (in pixels)
        self.b2 = b2
