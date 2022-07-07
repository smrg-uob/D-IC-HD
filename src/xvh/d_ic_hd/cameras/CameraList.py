from DummyCamera import DummyCamera as Dummy
from basler.BaslerCamera import BaslerCamera


class CameraList:
    # dummy camera
    dummy = Dummy()

    @staticmethod
    def get_dummy():
        print("Invalid camera requested, returning dummy camera")
        return CameraList.dummy

    def scan_cameras(self):
        self.cameras = BaslerCamera.available_cameras()
        return self

    def camera_count(self):
        return len(self.cameras)

    def create_camera(self, index):
        # safety checks
        if index < 0:
            return CameraList.get_dummy()
        if index >= len(self.cameras):
            return CameraList.get_dummy()
        # return an actual camera
        return BaslerCamera(self.cameras[index])

    def __init__(self):
        self.cameras = []
