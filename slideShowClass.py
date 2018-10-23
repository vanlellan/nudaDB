#Copyright 2018 Randall Evan McClellan

#This file is part of nudaDB.
#
#    nudaDB is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nudaDB is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nudaDB.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import tkinter as tk
from PIL import Image, ImageFile, ImageTk
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
import datetime
import pickle

#TODO
#	Make this class general enough to use for both import and slideshow
	#for import, text input bar sets tags for the current image
	#for slideshow, text input bar restarts slideshow with new search terms

#NUDADBDIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBDir/'		#this gets the directory of the python script
NUDADBDIR = os.getcwd() + '/nudaDBDir/'							#this gets the current working directory
#print NUDADBDIR
#NUDADBTABLE = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBTable.txt'
NUDADBTABLE = os.getcwd() + '/nudaDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def getImagesMatchingTags(listOfTags):
	with open("tags.pickle","rb") as pickleFile:
		tagDict = pickle.load(pickleFile)
	imagelist = []
	for tag in listOfTags:
		for result in tagDict[tag]:
			imagelist.append(result)
	return imagelist

class slideShowClass:
	def __init__(self,master,listOfImagePaths,showOrImport):
		self.master = master
		self.listOfImagePaths = listOfImagePaths
		self.showOrImport = showOrImport
		self.input_strings = []
		self.currentInputIndex = 0
		self.afterID = None
		self.currentImageIndex = -1
		self.rotations = {3: 180, 6: 270, 8: 90}
		#self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[0]))
		self.currentImage = None
		self.currentImageOriginal = None
		self.fullscreenState = True

		master.title("Slide Show")
		master.geometry(str(round(0.9*master.winfo_screenwidth()))+'x'+str(round(0.9*master.winfo_screenheight())))
		master.configure(background='black')
		self.master.attributes("-fullscreen", self.fullscreenState)

		self.showpanel = tk.Label(master, image=self.currentImage)
		self.showpanel.pack(fill='both', expand='yes')

		self.textbox = tk.Entry(master)
		self.textbox.focus()
		if self.showOrImport == 'show':
			self.textbox.bind("<Return>", self.new_search)
			self.textbox.bind("<Next>", self.show_next)	#Page Down
			#self.textbox.bind("<Prior>", self.show_prior)	#Page Up
			self.textbox.bind("<Up>", self.input_hist_prev)
			self.textbox.bind("<Down>", self.input_hist_next)
		elif self.showOrImport == 'import':
			self.textbox.bind("<Return>", self.send_tags)
			self.textbox.bind("<Up>", self.input_hist_prev)
			self.textbox.bind("<Down>", self.input_hist_next)
		self.textbox.bind("<Control-Key-w>", self.show_stop)
		self.textbox.bind("<Escape>", self.fullscreen_off)
		self.textbox.bind("<F11>", self.toggle_fullscreen)
		self.textbox.pack(side='bottom', fill='x', expand=True)

		if self.showOrImport == 'show':

			self.show_next()
		elif self.showOrImport == 'import':
			if self.next_image():
				self.tag_input()

	def fullscreen_off(self, event=None):
		self.fullscreenState = False
		self.master.attributes("-fullscreen", False)

	def toggle_fullscreen(self, event=None):
		self.fullscreenState = not self.fullscreenState
		self.master.attributes("-fullscreen", self.fullscreenState)

	def new_search(self, event=None):
		newTags = self.textbox.get()
		self.input_strings.append(newTags)
		taglist = self.input_strings[-1].split(' ')
		self.listOfImagePaths = getImagesMatchingTags(taglist)
		self.currentImageIndex = -1
		self.show_next()
		self.currentInputIndex = 0
		self.textbox.delete(0, tk.END)

	def getHash(self, thefile):
		BLOCKSIZE = 65536
		hasher = hashlib.md5()
		with open(thefile, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		return hasher.hexdigest()

	def input_hist_prev(self, event=None):
		self.currentInputIndex -= 1
		if self.currentInputIndex >= -len(self.input_strings):
			self.textbox.delete(0, tk.END)
			self.textbox.insert(0, self.input_strings[self.currentInputIndex])
		else:
			self.currentInputIndex += 1

	def input_hist_next(self, event=None):
		self.currentInputIndex += 1
		if self.currentInputIndex < 0:
			self.textbox.delete(0, tk.END)
			self.textbox.insert(0, self.input_strings[self.currentInputIndex])
		else:
			self.currentInputIndex = 0
			self.textbox.delete(0, tk.END)

	def send_tags(self, event=None):
		self.currentInputIndex = 0
		newTags = self.textbox.get()
		if newTags in ['\\quit', '\\exit', '\\abort']:
			self.master.quit()
			return None
		else:
			self.input_strings.append(newTags)
		taglist = self.input_strings[-1].split(' ')
		tags = ','.join(taglist)
		try:
			os.system("cp "+self.fullpath.replace(' ', "\ ")+" "+NUDADBDIR+self.month+str(self.dateAndTime.year)+'/'+self.newName)
			#Add entry to table
			with open(NUDADBTABLE, 'a') as table:
				table.write(self.newName+'\t'+'./nudaDBDir/'+self.month+str(self.dateAndTime.year)+'/'+'\t'+self.dateAndTime.strftime("%Y-%m-%d\t%H:%M:%S")+'\t'+tags+'\n')
			#if using default import, move file from ./inbox/ to ./inbox/imported/
			if os.path.isfile('./inbox/'+self.filename):
				os.system("mv "+self.fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/imported/"+self.newName)
		except:
			print("copy problem!")
		self.textbox.delete(0, tk.END)
		if self.next_image():
			self.tag_input()

	def tag_input(self, event=None):
		#Get file data
		self.fullpath = os.path.abspath(self.listOfImagePaths[self.currentImageIndex])
		self.filename = self.fullpath.split('/')[-1]
		extension = self.filename.split('.')[-1]
		self.dirpath = self.fullpath[:-len(self.filename)]
		try:
			fullexif=self.currentImageOriginal._getexif()
			self.dateAndTime = datetime.datetime.strptime(fullexif[36867], "%Y:%m:%d %H:%M:%S")
		except Exception as ex:
			print(ex)
			print("EXIF problem! Using file timestamp...")
			try:
				self.dateAndTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.fullpath))
			except Exception as ex:	
				print(ex)
				print("No file timestamp!? Crashing...")
				self.master.quit()
				return None
	
		self.month = MONTHS[self.dateAndTime.month-1]
		#check for existing month directory, create if not exists
		dirContents = os.listdir(NUDADBDIR)
		dirCheck = NUDADBDIR+self.month+str(self.dateAndTime.year)
		if self.month+str(self.dateAndTime.year) in dirContents:
			pass
			#print(dirCheck+'/'+"  exists!")
		else:
			print("Creating "+dirCheck)
			os.system("mkdir "+dirCheck)
	
		#copy file     filename = last six characters of hashstring
		monthContents = os.listdir(NUDADBDIR+self.month+str(self.dateAndTime.year))
		fullHash = self.getHash(self.fullpath)
		self.newName = fullHash[-6:]+'.'+extension
		if self.newName in monthContents:
			print("COLLISION!     Skipping...")
			#if using default import, move file from ./inbox/ to ./inbox/imported/
			if os.path.isfile('./inbox/'+self.filename):
				os.system("mv "+self.fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/"+self.newName)
			if self.next_image():
				self.tag_input()

	def next_image(self, event=None):
		if self.afterID is not None:
			self.master.after_cancel(self.afterID)
			self.afterID = None
		self.currentImageIndex += 1
		if self.currentImageIndex >= len(self.listOfImagePaths):
			if self.showOrImport == 'show':
				self.currentImageIndex = 0
			elif self.showOrImport == 'import':
				self.master.quit()
				return False
			else:
				print("Something has gone very wrong...")
				self.master.quit()
				return False
		self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[self.currentImageIndex]))
		self.showpanel.configure(image=self.currentImage)
		self.showpanel.image = self.currentImage
		return True

	def show_next(self, event=None):
		self.next_image(event)
		self.afterID = self.master.after(2000,self.show_next)

	def show_stop(self, event):
		self.master.quit()

	def makeThumb(self, imagePath):
		thumb = Image.open(imagePath)
		self.currentImageOriginal = Image.open(imagePath)
		try:
			orientation = thumb._getexif()[0x0112]
		except:
			print("EXIF problem! Setting orientation=0")
			orientation = 0
		if orientation in self.rotations:
			thumb = thumb.rotate(self.rotations[orientation], expand=1)
		self.master.update_idletasks()
		thumb.thumbnail((self.master.winfo_width(),self.master.winfo_height()-50))
		return thumb
		

