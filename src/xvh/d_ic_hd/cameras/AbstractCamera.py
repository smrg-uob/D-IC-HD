class AbstractCamera:
    def __init__(self, logger):
        self.logger = logger
        pass

    def get_name(self):
        pass

    def is_valid(self):
        pass

    def grab_picture(self):
        pass

    def set_exposure(self, exposure):
        pass

    def get_exposure(self):
        pass

    def min_exposure(self):
        pass

    def max_exposure(self):
        pass

    def log(self, line):
        self.logger(line)
