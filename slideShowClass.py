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
import vlc
import os
import datetime
import pickle
import random

NUDADBDIR = os.getcwd()+'/nudaDBDir/'
NUDADBTABLE = os.getcwd()+'/nudaDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def getHash(thefile):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(thefile, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def getImagesMatchingTags(listOfTags):
    with open("tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
    imagelist = []
    for tag in listOfTags:
        for result in tagDict[tag]:
            imagelist.append(result)
    return imagelist

def myPlay(aPlayer):
    aPlayer.set_media(aPlayer.get_media())
    aPlayer.play()

class slideShowClass:
    def __init__(self,master,listOfImagePaths,showOrImport):
        self.master = master
        self.listOfImagePaths = listOfImagePaths
        self.showOrImport = showOrImport

        self.input_strings = []
        self.currentInputIndex = 0

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
        self.frameVid = tk.Frame(master, width=600, height=400)
        self.frameImg.place(anchor='center', rely=0.5, relx=0.5)
        self.showpanel = tk.Label(self.frameImg, image=self.currentTkImage)
        self.showpanel.pack()
        self.frameImg.grid(row=0, column=0, sticky="news")  #what does sticky do?
        self.frameVid.grid(row=0, column=0, sticky="news")
        self.frameButtons.grid(row=1, column=0)
        self.qButton = tk.Button(self.frameButtons, text="Quit", command=master.destroy)
        self.qButton.pack()

        #set up vlc video player
        self.vlcInstance = vlc.Instance()
        self.vlcPlayer = self.vlcInstance.media_player_new()
        self.vlcPlayer.set_xwindow(self.frameVid.winfo_id())   #connect vlc to tk
        #self.pButton = tk.Button(self.frameButtons, text="Play", command=lambda:myPlay(self.vlcPlayer))
        self.pButton = tk.Button(self.frameButtons, text="Play", command=lambda:self.playVid())
        self.pButton.pack()

        self.textbox = tk.Entry(self.frameButtons)
        self.textbox.focus()
        self.textbox.bind("<Return>", self.send_tags)
        self.textbox.bind("<Control-Key-w>", self.show_stop)
        self.textbox.bind("<Control-Key-p>", self.playVid)
        self.textbox.bind("<Up>", self.input_hist_prev)
        self.textbox.bind("<Down>", self.input_hist_next)
        self.textbox.pack(side='bottom', fill='x', expand=True)

        while not self.setup_next_input():
            print(self.listOfImagePaths[self.currentImageIndex], "has been skipped!")

        if self.showOrImport == 'import':
            pass
        else:
            print("Non-Import Currently Disabled!")
            self.master.quit()

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

    def playVid(self, event=None):
        self.vlcPlayer.set_media(self.vlcPlayer.get_media())
        self.vlcPlayer.play()

    def show_stop(self, event):
        self.master.quit()

    def send_tags(self, event=None):
        #write table entry and import file
        self.newTags = self.textbox.get()
        if self.newTags in ['\\quit', '\\exit', '\\abort']:
            self.master.quit()
            return None
        else:
            self.input_strings.append(self.newTags)
        taglist = self.newTags.split(' ')
        tags = ','.join(taglist)
        try:
            os.system("cp "+self.fullpaths[self.currentImageIndex].replace(' ', "\ ")+" "+NUDADBDIR+self.month+self.year+'/'+self.newName)
            #Add entry to table
            with open(NUDADBTABLE, 'a') as table:
                table.write(self.newName+'\t'+'./nudaDBDir/'+self.month+self.year+'/'+'\t'+self.dateAndTimes[self.currentImageIndex].strftime("%Y-%m-%d\t%H:%M:%S")+'\t'+tags+'\n')
            #if using default import, move file from ./inbox/ to ./inbox/imported/
            if os.path.isfile('./inbox/'+self.filenames[self.currentImageIndex]):
                os.system("mv "+self.fullpaths[self.currentImageIndex].replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/imported/")
        except Exception as ex:
            print("copy problem!")
            print(ex)
        #setup next input file
        self.textbox.delete(0, tk.END)
        while not self.setup_next_input():
            print(self.listOfImagePaths[self.currentImageIndex], "has been skipped!")
        return True

    def assess_all_images(self):
        self.assessments = [None for f in self.listOfImagePaths]
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
                self.assessments[i] = "Image"
            except Exception as ex:
                print("Can't open "+f+"... Not an image!")
                print(ex)
        #check the rest to see if they have known video format extensions
        for i,a in enumerate(self.assessments):
            if a is None:
                if self.extensions[i] in ["mp4","avi","AVI","3g2","MPG","mpg","wmv","MOV"]:
                    self.assessments[i] = "Video"
        #get EXIF date and time for files assessed as images
        for i,a in enumerate(self.assessments):
            if a == "Image":
                try:
                    testOpen = Image.open(self.fullpaths[i])
                    fullexif=testOpen._getexif()
                    self.dateAndTimes[i] = datetime.datetime.strptime(fullexif[36867], "%Y:%m:%d %H:%M:%S")
                except Exception as ex:
                    print("EXIF problem! Using file timestamp...")
                    print(ex)
                    try:
                        self.dateAndTimes[i] = datetime.datetime.fromtimestamp(os.path.getmtime(self.fullpaths[i]))
                    except Exception as ex:    
                        print("No file timestamp!? Crashing...")
                        print(ex)
                        self.master.quit()
            elif a == "Video":
                print("WARNING: using file timestamp for video for now!")   #maybe use an external call to exiftool?
                try:
                    self.dateAndTimes[i] = datetime.datetime.fromtimestamp(os.path.getmtime(self.fullpaths[i]))
                except Exception as ex:    
                    print("No file timestamp!? Crashing...")
                    print(ex)
                    self.master.quit()

        print("DEBUG: dateAndTimes = ", self.dateAndTimes)
        print("DEBUG: assessments = ", self.assessments)

    def setup_next_input(self, event=None):
        self.currentImageIndex += 1
        if self.currentImageIndex >= len(self.fullpaths):
            self.master.quit()
            print("DEBUG: ALL DONE")
            return True
        print("DEBUG: index = ", self.currentImageIndex)
        if self.assessments[self.currentImageIndex] is not None:
            print("DEBUG GOT HERE IF")
            #check target DIR
            self.month = MONTHS[self.dateAndTimes[self.currentImageIndex].month-1]
            self.year = str(self.dateAndTimes[self.currentImageIndex].year)
            dirContents = os.listdir(NUDADBDIR)
            dirCheck = NUDADBDIR+self.month+str(self.dateAndTimes[self.currentImageIndex].year)
            if self.month+str(self.dateAndTimes[self.currentImageIndex].year) in dirContents:
                pass
            else:
                print("Creating "+dirCheck)
                os.system("mkdir "+dirCheck)
            #check for collisions
            monthContents = os.listdir(NUDADBDIR+self.month+self.year)
            fullHash = getHash(self.fullpaths[self.currentImageIndex])
            self.newName = fullHash[-6:]+'.'+self.extensions[self.currentImageIndex]
            if self.newName in monthContents:
                print("COLLISION!     Skipping...")
                #if using default import, move file from ./inbox/ to ./inbox/skipped/
                if os.path.isfile('./inbox/'+self.filenames[self.currentImageIndex]):
                    os.system("mv "+self.fullpaths[self.currentImageIndex].replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/")
                    return False
        if self.assessments[self.currentImageIndex] == "Image":
            self.currentImage = Image.open(self.fullpaths[self.currentImageIndex]).resize((600,400), Image.ANTIALIAS)
            self.currentTkImage = ImageTk.PhotoImage(image=self.currentImage)
            self.showpanel.config(image = self.currentTkImage)
            self.frameImg.tkraise()
        elif self.assessments[self.currentImageIndex] == "Video":
            self.frameVid.tkraise()
            self.vlcMedia = self.vlcInstance.media_new(self.fullpaths[self.currentImageIndex])
            self.vlcPlayer.set_media(self.vlcMedia)
        else:
            print("DEBUG GOT HERE ELSE")
            os.system("mv "+self.fullpaths[self.currentImageIndex].replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/")
            return False
        return True
