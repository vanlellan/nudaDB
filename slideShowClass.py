#Copyright 2022 Randall Evan McClellan

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
import random

NUDADBDIR = os.getcwd()+'/nudaDBDir/'
NUDADBTABLE = os.getcwd()+'/nudaDBTable.txt'
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

        self.currentTkImage = None
        self.currentImageIndex = -1

        master.title("Slide Show")
        #master.geometry(str(round(0.9*master.winfo_screenwidth()))+'x'+str(round(0.9*master.winfo_screenheight())))
        master.geometry('600x500')
        master.configure(background='black')

        self.assess_all_images()

        print("DEBUG currentTkImage = ", self.currentTkImage)

        self.frameButtons = tk.Frame(master, width=600, height=100)
        self.frameImg = tk.Frame(master, width=600, height=400)
        self.frameImg.place(anchor='center', rely=0.5, relx=0.5)
        self.showpanel = tk.Label(self.frameImg, image=self.currentTkImage)
        self.showpanel.pack()
        self.frameImg.grid(row=0, column=0)
        self.frameButtons.grid(row=1, column=0)
        self.qButton = tk.Button(self.frameButtons, text="Quit", command=master.destroy)
        self.qButton.pack()

        #self.showpanel = tk.Label(master, image=self.currentTkImage)
        #self.showpanel.pack(fill='both', expand='yes')
        #self.showpanel.pack()

        self.textbox = tk.Entry(self.frameButtons)
        self.textbox.focus()
        self.textbox.bind("<Return>", self.send_tags)
        self.textbox.bind("<Control-Key-w>", self.show_stop)
        self.textbox.pack(side='bottom', fill='x', expand=True)

        self.setup_next_input()

        if self.showOrImport == 'import':
            pass
        else:
            print("Non-Import Currently Disabled!")
            self.master.quit()

    def show_stop(self, event):
        self.master.quit()

    def send_tags(self, event=None):
        print("SENDING TAGS")
        print("SETTING UP NEXT IMAGE")
        self.setup_next_input()

    def assess_all_images(self):
        self.assessments = ["Image" for f in self.listOfImagePaths]
        self.dateAndTimes = [None for f in self.listOfImagePaths]
        #Get file data
        self.fullpaths = [os.path.abspath(f) for f in self.listOfImagePaths]
        self.filenames = [f.split('/')[-1] for f in self.fullpaths]
        self.extensions = [f.split('.')[-1] for f in self.filenames]
        self.dirpaths = [f[:-len(self.filenames[i])] for i,f in enumerate(self.fullpaths)]
        #try to open all files as images
        for i,f in enumerate(self.fullpaths):
            testOpen = None
            try:
                testOpen = Image.open(f)
                testTkImage = ImageTk.PhotoImage(testOpen)
            except Exception as ex:
                print(ex)
                print("Can't open "+f+"... Not an image!")
                self.assessments[i] = None
            try:
                fullexif=testOpen._getexif()
                self.dateAndTimes[i] = datetime.datetime.strptime(fullexif[36867], "%Y:%m:%d %H:%M:%S")
            except Exception as ex:
                print(ex)
                print("EXIF problem! Using file timestamp...")
                try:
                    self.dateAndTimes[i] = datetime.datetime.fromtimestamp(os.path.getmtime(self.fullpaths[i]))
                except Exception as ex:    
                    print(ex)
                    print("No file timestamp!? Crashing...")
                    self.master.quit()
        print("DEBUG: dateAndTimes = ", self.dateAndTimes)

    def setup_next_input(self, event=None):
        self.currentImageIndex += 1
        if self.currentImageIndex >= len(self.fullpaths):
            self.master.quit()
            print("DEBUG: ALL DONE")
            return False
        print("DEBUG: index = ", self.currentImageIndex)
        if self.assessments[self.currentImageIndex] == "Image":
            print("DEBUG GOT HERE IF")
            self.currentImage = Image.open(self.fullpaths[self.currentImageIndex]).resize((600,400), Image.ANTIALIAS)
            self.currentTkImage = ImageTk.PhotoImage(image=self.currentImage)
            self.showpanel.config(image = self.currentTkImage)
            #self.currentTkImage = ImageTk.PhotoImage(file=self.fullpaths[self.currentImageIndex])
        else:
            print("DEBUG GOT HERE ELSE")
            self.setup_next_input()
        return True

        #loop of mystery
#        def show_next(self, event=None):
#            self.next_image(event)              #call next_image, passing event
#            self.afterID = self.master.after(2000, self.show_next)      #after 2000?, call show_next again, saving afterID
#
#        def next_image(self, event=None):
#            #cancel after mechanism?
#            #check if this no more files
#            #open file as image
#            #show image with tk
#            #return true
#
#        def send_tags(self, event=None):
#            #mapped to Return key
#
#        def tag_input(self, event=None):
#            #prepare to send tags for current image
#            #get path, filename, and extension
#            #get exif info
#            #check if month dir exists, if not, create it
#            #get Hash, create new filename
#            #check for collisions
#            #call for next image

