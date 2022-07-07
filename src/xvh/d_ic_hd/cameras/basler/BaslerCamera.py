from xvh.d_ic_hd.cameras.AbstractCamera import AbstractCamera
from pypylon import pylon
import numpy as np


class BaslerCamera(AbstractCamera):
    @staticmethod
    def available_cameras(logger):
        baslers = pylon.TlFactory.GetInstance().EnumerateDevices()
        cameras = []
        for basler in baslers:
            cameras.append(BaslerCamera(basler, logger))
        return cameras

    def is_valid(self):
        return True

    def get_name(self):
        return "Basler " + self.info.GetSerialNumber()

    def grab_picture(self):
        self.camera.Open()
        self.camera.ExposureTime.Value = self.exposure
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

    def get_exposure(self):
        return self.exposure

    def min_exposure(self):
        return self.min_exp

    def max_exposure(self):
        return self.max_exp

    def __init__(self, camera_info, logger):
        AbstractCamera.__init__(self, logger)
        self.info = camera_info
        self.device = pylon.TlFactory.GetInstance().CreateDevice(camera_info)
        self.camera = pylon.InstantCamera(self.device)
        self.camera.Open()
        self.min_exp = int(self.camera.ExposureTime.Min)
        self.max_exp = int(self.camera.ExposureTime.Max)
        self.exposure = self.min_exp
        self.set_exposure(self.min_exp)
        self.camera.Close()
