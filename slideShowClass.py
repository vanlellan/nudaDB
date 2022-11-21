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
import random

#Updating to do resurrect slideshow only -- REM -- 2022-11-16

#TODO
#    Make this class general enough to use for both import and slideshow
    #for import, text input bar sets tags for the current image
    #for slideshow, text input bar restarts slideshow with new search terms
    #fix final skipped file in a batch of duplicates getting tag input anyway
    #for import, sort inbox files by timestamp

#NUDADBDIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBDir/'        #this gets the directory of the python script
NUDADBDIR = os.getcwd() + '/nudaDBDir/'                            #this gets the current working directory
#print NUDADBDIR
#NUDADBTABLE = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBTable.txt'
NUDADBTABLE = os.getcwd() + '/nudaDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
DELAY = 5000    #time delay to display each image in milliseconds

def getFilesMatchingAllTags(listOfTags):
    #SLIDESHOW VERSION, RETURN LIST OF STRINGS, NOT LIST OF TUPLES
    #HARDCODE RETURN ONLY IMAGES
    listOfTags.append("image")
    with open("./tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
    aFileList = []
    outputList = []
    #get all files matching first tag
    for result in tagDict[listOfTags[0]]:
        aFileList.append(result)
    #loop through other tags, keeping only files which match
    for tag in listOfTags[1:]:
        aFileList = [f for f in aFileList if f in tagDict[tag]]
    #loop through final list, sorting image, video, and other, and specifying ext
    #for result in aFileList:
    #    ext = result.split('.')[-1]
    #    if result in tagDict['image']:
    #        outputList.append((result,'image',ext))
    #    elif result in tagDict['video']:
    #        outputList.append((result,'video',ext))
    #    else:
    #        outputlist.append((result,'other',ext))
    print(f"Found {len(aFileList)} Images matching tags: {listOfTags}")
    return aFileList

def getImagesMatchingTags(listOfTags):
    with open("tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
    imagelist = []
    for tag in listOfTags:
        for result in tagDict[tag]:
            imagelist.append(result)
    return imagelist

class slideShowClass:
    #def __init__(self,master,listOfImagePaths,showOrImport):
    def __init__(self,master,listOfImagePaths):
        self.master = master
        self.listOfImagePaths = listOfImagePaths
        self.input_strings = []
        self.currentInputIndex = 0
        self.afterID = None
        self.currentImageIndex = -1
        self.rotations = {3: 180, 6: 270, 8: 90}
        #self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[0]))
        self.currentImage = None
        self.currentImageOriginal = None
        self.fullscreenState = True

        #self.sortImageListByTimeStamp()
        self.sortImageListByShuffle()

        master.title("Slide Show")
        master.geometry(str(round(0.9*master.winfo_screenwidth()))+'x'+str(round(0.9*master.winfo_screenheight())))
        master.configure(background='black')
        self.master.attributes("-fullscreen", self.fullscreenState)

        self.showpanel = tk.Label(master, image=self.currentImage)
        self.showpanel.pack(fill='both', expand='yes')
        self.showpanel.config(bg="black")

        self.textbox = tk.Entry(master)
        self.textbox.focus()
        self.textbox.bind("<Return>", self.new_search)
        self.textbox.bind("<Next>", self.show_next)    #Page Down
        self.textbox.bind("<Prior>", self.show_prev)    #Page Up
        self.textbox.bind("<Up>", self.input_hist_prev)
        self.textbox.bind("<Down>", self.input_hist_next)
        self.textbox.bind("<Control-Key-w>", self.show_stop)
        self.textbox.bind("<Escape>", self.fullscreen_off)
        self.textbox.bind("<F11>", self.toggle_fullscreen)
        self.textbox.pack(side='bottom', fill='x', expand=True)

        self.show_next()

    def sortImageListByShuffle(self, event=None):
        random.shuffle(self.listOfImagePaths)

    def sortImageListByTimeStamp(self, event=None):
        idummy = 1
        tempList = self.listOfImagePaths
        stamps = []
        for impath in tempList:
            aImage = Image.open(impath)
            try:
                fullexif=aImage._getexif()
                aTime = datetime.datetime.strptime(fullexif[36867], "%Y:%m:%d %H:%M:%S")
                stamps.append(int(aTime.timestamp()))
            except Exception as ex:
                print(ex)
                print("EXIF Problem! Assigning unix timestamp as ", idummy)
                stamps.append(idummy)
                idummy = idummy + 1
        sortedList = [x for _, x in sorted(zip(stamps,tempList), key=lambda pair: pair[0])]
        self.listOfImagePaths = list(sortedList)

    def fullscreen_off(self, event=None):
        self.fullscreenState = False
        self.master.attributes("-fullscreen", False)

    def toggle_fullscreen(self, event=None):
        self.fullscreenState = not self.fullscreenState
        self.master.attributes("-fullscreen", self.fullscreenState)

    def new_search(self, event=None):
        newTags = self.textbox.get()
        if newTags in ['\\quit', '\\exit', '\\abort']:
            self.master.quit()
            return None
        self.input_strings.append(newTags)
        taglist = self.input_strings[-1].split(' ')
        self.listOfImagePaths = getFilesMatchingAllTags(taglist)
        self.sortImageListByShuffle()
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

    def next_image(self, event=None):
        if self.afterID is not None:
            self.master.after_cancel(self.afterID)
            self.afterID = None
        self.currentImageIndex += 1
        if self.currentImageIndex >= len(self.listOfImagePaths):
            self.currentImageIndex = 0
        try:
            tempFileName = self.listOfImagePaths[self.currentImageIndex]
            testOpen = Image.open(tempFileName)
        except:
            print("Can't open file: "+tempFileName+" (Not an image?) Skipping....")
            if os.path.isfile('./inbox/'+self.filename):
                os.system("mv "+self.fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/"+self.newName)
            else:
                print("Can't find file to skip!? Something has gone wrong...")
            return False    #skip tag input for this skipped file
        self.currentImage = ImageTk.PhotoImage(self.makeThumb(self.listOfImagePaths[self.currentImageIndex]))
        self.showpanel.configure(image=self.currentImage)
        self.showpanel.image = self.currentImage
        return True

    def show_next(self, event=None):
        self.next_image(event)
        self.afterID = self.master.after(DELAY,self.show_next)

    def show_prev(self, event=None):
        self.currentImageIndex = max(0,self.currentImageIndex-2)
        self.next_image(event)
        self.afterID = self.master.after(DELAY,self.show_next)

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
