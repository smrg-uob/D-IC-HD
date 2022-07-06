from Camera import Camera
import numpy as np


# Dummy Camera object for when there are no cameras available
class DummyCamera(Camera):
    def is_valid(self):
        return False

    def set_exposure(self, exposure):
        pass

    def grab_picture(self):
        return self.img

    def __init__(self):
        self.img = np.zeros((1, 1), dtype=np.uint8)