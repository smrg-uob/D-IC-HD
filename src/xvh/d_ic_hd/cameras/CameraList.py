from DummyCamera import DummyCamera as Dummy
from basler.BaslerCamera import BaslerCamera


class CameraList:

    def scan_cameras(self):
        self.cameras = BaslerCamera.available_cameras(self.logger)
        return self

    def camera_count(self):
        return len(self.cameras)

    def create_camera(self, index):
        # safety checks
        if index < 0:
            return self.dummy
        if index >= len(self.cameras):
            return self.dummy
        # return an actual camera
        return self.cameras[index]

    def __init__(self, logger):
        self.cameras = []
        self.logger = logger
        self.dummy = Dummy(logger)
