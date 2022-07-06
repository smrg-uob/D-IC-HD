from pypylon import pylon
import numpy as np


class Camera:
    def is_valid(self):
        return True

    def grab_picture(self):
        self.camera.Open()
        self.camera.ExposureTime.value = self.exposure
        self.camera.StartGrabbing(1)
        grabbed = self.camera.RetrieveResult(5*self.exposure, pylon.TimeoutHandling_ThrowException)
        if grabbed.GrabSucceeded():
            img = grabbed.Array
        else:
            img = np.zeros((self.camera.Height.Value, self.camera.Width.Value), dtype=np.uint8)
        grabbed.Release()
        self.camera.Close()
        return img

    def set_exposure(self, exposure):
        self.exposure = exposure
        return self

    def __init__(self, camera_info):
        self.info = camera_info
        self.device = pylon.TlFactory.GetInstance().CreateDevice(camera_info)
        self.camera = pylon.InstantCamera(self.device)
        self.camera.Open()
        self.min_exp = self.camera.ExposureTime.Min
        self.max_exp = self.camera.ExposureTime.Max
        self.exposure = self.min_exp
        self.set_exposure(self.min_exp)
        self.camera.Close()