
import tkinter as tk
from PIL import Image, ImageFile, ImageTk


#TODO
#	Make this class general enough to use for both import and slideshow
	#for import, text input bar sets tags for the current image
	#for slideshow, text input bar restarts slideshow with new search terms

class slideShowClass:
	def __init__(self,master,listOfImagePaths):
		self.master = master
		self.listOfImagePaths = listOfImagePaths
		self.afterID = None
		self.currentIndex = 0
		self.rotations = {3: 180, 6: 270, 8: 90}
		self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[0]))

		master.title("Slide Show")
		master.geometry("800x800")
		master.configure(background='black')

		self.showpanel = tk.Label(master, image=self.currentImage)
		self.showpanel.focus_set()
		self.showpanel.bind("<Escape>", self.show_stop)
		self.showpanel.bind("<space>", self.show_next)
		self.showpanel.pack(fill='both', expand='yes')
		self.afterID = self.master.after(2000,self.show_next)

	def show_next(self, event=None):
		if self.afterID is not None:
			self.master.after_cancel(self.afterID)
			self.afterID = None
		self.currentIndex += 1
		if self.currentIndex >= len(self.listOfImagePaths):
			self.currentIndex = 0
		self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[self.currentIndex]))
		self.showpanel.configure(image=self.currentImage)
		self.showpanel.image = self.currentImage
		self.afterID = self.master.after(2000,self.show_next)

	def show_stop(self, event):
		self.master.destroy()

	def makeThumb(self, imagePath):
		thumb = Image.open(imagePath)
		try:
			orientation = thumb._getexif()[0x0112]
		except:
			print("EXIF problem!")
			orientation = 0
		if orientation in self.rotations:
			thumb = thumb.rotate(self.rotations[orientation], expand=1)
		thumb.thumbnail((800,800))
		return thumb
		

