from AbstractCamera import AbstractCamera
import numpy as np
from PIL import Image


# Test Camera object for when there are no cameras available
class TestCamera(AbstractCamera):
    def is_valid(self):
        return True

    def get_name(self):
        return "Test Camera"

    def grab_picture(self):
        return self.img

    def set_exposure(self, exposure):
        return self

    def get_exposure(self):
        return 0

    def min_exposure(self):
        return 0

    def max_exposure(self):
        return 0

    def __init__(self, logger):
        AbstractCamera.__init__(self, logger)
        image = Image.open("resources/test_image.png")
        self.img = np.asarray(image)
