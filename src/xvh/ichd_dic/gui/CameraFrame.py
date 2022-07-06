import Tkinter as Tk
from Tkinter import Frame
from Tkinter import Label
from PIL import Image, ImageTk


# Class to display an image on a frame
class CameraFrame(Frame):
    def __init__(self, master, camera, *pargs):
        Frame.__init__(self, master, *pargs)
        # set the camera
        self.camera = camera
        # set the width and height
        self.w = 300
        self.h = 300
        # take an image, and copy and resize it
        self.original = Image.fromarray(self.camera.grab_picture())
        self.image = self.original.copy().resize((self.w, self.h))
        # set the background image and bind the resize method to it
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=Tk.BOTH, expand=Tk.YES)
        self.background.bind('<Configure>', self._resize_image)

    def refresh_image(self):
        # take a new picture
        self.original = Image.fromarray(self.camera.grab_picture())
        # resize it
        self.image = self.original.copy().resize((self.w, self.h))
        # set it as the background
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)

    def _resize_image(self, event):
        # fetch new width and height
        self.w = event.width
        self.h = event.height
        # resize
        self.image = self.original.copy().resize((self.w, self.h))
        # set the new background
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)
