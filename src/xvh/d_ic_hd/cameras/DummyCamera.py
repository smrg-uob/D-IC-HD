from AbstractCamera import AbstractCamera
import numpy as np


# Dummy Camera object for when there are no cameras available
class DummyCamera(AbstractCamera):
    def is_valid(self):
        return False

    def get_name(self):
        return "dummy"

    def grab_picture(self):
        return self.img

    def set_exposure(self, exposure):
        return self

    def __init__(self, logger):
        AbstractCamera.__init__(self, logger)
        self.img = np.zeros((1, 1), dtype=np.uint8)