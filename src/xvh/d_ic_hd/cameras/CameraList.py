from DummyCamera import DummyCamera as Dummy
from basler.BaslerCamera import BaslerCamera


class CameraList:

    def scan_cameras(self):
        self.cameras = []
        self.names = []
        for camera in BaslerCamera.available_cameras(self.logger):
            self.cameras.append(camera)
            self.names.append(camera.get_name())
        return self

    def camera_count(self):
        return len(self.cameras)

    def get_names(self):
        return self.names

    def get_camera(self, index):
        # safety checks
        if index < 0:
            return self.dummy
        if index >= len(self.cameras):
            return self.dummy
        # return an actual camera
        return self.cameras[index]

    def __init__(self, logger):
        self.cameras = []
        self.names = []
        self.logger = logger
        self.dummy = Dummy(logger)
