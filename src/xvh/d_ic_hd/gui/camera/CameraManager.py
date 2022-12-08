# coding=utf-8

import threading


# Class to capture images in a separate thread
class CameraManager:
    def __init__(self, camera):
        self.camera = camera
        self.img = None
        self.capturing = False

    def imaging_thread_func(self):
        self.capturing = True
        self.img = self.camera.grab_picture()
        self.capturing = False

    def capture_image(self):
        # check if there is already an image
        if self.is_capturing() or self.has_captured():
            # return false indicating we can not yet capture
            return False
        # make sure the previous image is cleared
        self.img = None
        # start a new thread
        threading.Thread(target=self.imaging_thread_func).start()
        # return true indicating capturing has started
        return True

    def is_capturing(self):
        return self.capturing

    def has_captured(self):
        return self.img is not None

    def grab_image(self):
        image = self.img
        self.img = None
        return image
