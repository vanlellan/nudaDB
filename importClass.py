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
import subprocess

NUDADBDIR = os.getcwd()+'/nudaDBDir/'
NUDADBTABLE = os.getcwd()+'/nudaDBTable.txt'
MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']

def getHash(thefile):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(thefile, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

#def getImagesMatchingTags(listOfTags):
#    with open("tags.pickle","rb") as pickleFile:
#        tagDict = pickle.load(pickleFile)
#    imagelist = []
#    for tag in listOfTags:
#        for result in tagDict[tag]:
#            imagelist.append(result)
#    return imagelist

def myPlay(aPlayer):
    aPlayer.set_media(aPlayer.get_media())
    aPlayer.play()

class importClass:
    def __init__(self,master,listOfImagePaths):
        self.master = master
        self.data = [{"path":a} for a in listOfImagePaths]

        self.input_strings = []
        self.currentInputIndex = 0

        self.currentTkImage = None
        self.currentImageIndex = -1

        self.width = 1200
        self.height = 800
        self.boxHeight = 65

        master.title("Nuda Import")
        #master.geometry(str(round(0.9*master.winfo_screenwidth()))+'x'+str(round(0.9*master.winfo_screenheight())))
        master.geometry(str(self.width)+'x'+str(self.height+self.boxHeight))
        master.configure(background='black')

        self.assess_all_images()

        #sort input files according to datetime
        self.data.sort(key=lambda d: d["datetime"])

        self.frameButtons = tk.Frame(master, width=self.width, height=self.boxHeight)
        self.frameImg = tk.Frame(master, width=self.width, height=self.height)
        self.frameVid = tk.Frame(master, width=self.width, height=self.height)
        self.frameImg.place(anchor='center', rely=0.5, relx=0.5)
        self.showpanel = tk.Label(self.frameImg, image=self.currentTkImage)
        self.showpanel.pack()
        self.frameImg.grid(row=0, column=0, sticky="news")  #what does sticky do?
        self.frameVid.grid(row=0, column=0, sticky="news")
        self.frameButtons.grid(row=1, column=0)
        self.qButton = tk.Button(self.frameButtons, text="Quit", command=master.destroy)
        self.qButton.pack(side='left')

        #set up vlc video player
        self.vlcInstance = vlc.Instance()
        self.vlcPlayer = self.vlcInstance.media_player_new()
        self.vlcPlayer.set_xwindow(self.frameVid.winfo_id())   #connect vlc to tk
        #self.pButton = tk.Button(self.frameButtons, text="Play", command=lambda:myPlay(self.vlcPlayer))
        self.pButton = tk.Button(self.frameButtons, text="Restart", command=lambda:self.playVid())
        self.pButton.pack(side='right')

        #current file Label
        self.label = tk.Label(self.frameButtons, text="Importing File: ???")
        self.label.pack(side='top')

        #tag input textbox
        self.textbox = tk.Entry(self.frameButtons, width=int(self.width/10))
        self.textbox.focus()
        self.textbox.bind("<Return>", self.send_tags)
        self.textbox.bind("<Control-Key-w>", self.show_stop)
        self.textbox.bind("<Control-Key-p>", self.togglePlay)
        self.textbox.bind("<Control-Key-0>", self.volumeMax)
        self.textbox.bind("<Up>", self.input_hist_prev)
        self.textbox.bind("<Down>", self.input_hist_next)
        self.textbox.pack(side='top', fill='x', expand=True)

        #Editable datetime textbox
        self.datebox = tk.Entry(self.frameButtons, width=int(self.width/10))
        self.datebox.bind("<Return>", self.send_tags)
        self.datebox.bind("<Control-Key-w>", self.show_stop)
        self.datebox.pack(side='top', fill='x', expand=True)

        #Tooltip Hover Text
        #self.pTip = tk.tix.Balloon(master)
        #self.pTip.bind_widget(self.pButton, balloonmsg="Ctrl-p")
        #self.qTip = tk.tix.Balloon(master)
        #self.qTip.bind_widget(self.qButton, balloonmsg="Ctrl-w")

        while not self.setup_next_input():
            print(self.data[self.currentImageIndex]['path'], "has been skipped!")

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

    def createTargetDir(self, event=None):
        #self.month = MONTHS[self.data[self.currentImageIndex]["datetime"].month-1]
        self.month = str(self.data[self.currentImageIndex]["datetime"].month).zfill(2)
        self.year = str(self.data[self.currentImageIndex]["datetime"].year)
        dirContents = os.listdir(NUDADBDIR)
        dirCheck = NUDADBDIR+self.year+'-'+self.month
        if self.year+'-'+self.month in dirContents:
            pass
        else:
            print("Creating "+dirCheck)
            os.system("mkdir "+dirCheck)

    def checkForCollisions(self, event=None):
        monthContents = os.listdir(NUDADBDIR+self.year+'-'+self.month)
        #strip off extension so that 'jpg' and 'JPG' and 'jpeg' will collide
        monthContents = [x.split('.')[0] for x in monthContents]
        fullHash = getHash(self.data[self.currentImageIndex]["fullpath"])
        hashTail = fullHash[-6:]
        self.newName = hashTail+'.'+self.data[self.currentImageIndex]["extension"]
        if hashTail in monthContents:
            print("COLLISION!     Skipping...")
            #if using default import, move file from ./inbox/ to ./inbox/skipped/
            if os.path.isfile('./inbox/'+self.data[self.currentImageIndex]["filename"]):
                os.system("mv "+self.data[self.currentImageIndex]["fullpath"].replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/")
                return True

    def playVid(self, event=None):
        self.vlcPlayer.set_media(self.vlcPlayer.get_media())
        self.vlcPlayer.play()

    def togglePlay(self, event=None):
        if self.vlcPlayer.is_playing():
            self.vlcPlayer.pause()
        else:
            self.vlcPlayer.play()

    def volumeMax(self, event=None):
        self.vlcPlayer.audio_set_volume(100)

    def show_stop(self, event):
        self.master.quit()

    def send_tags(self, event=None):
        self.vlcPlayer.stop()
        #update datetime from datebox
        newDateTime = self.datebox.get()
        try:
            self.data[self.currentImageIndex]["datetime"] = datetime.datetime.strptime(newDateTime, "%Y:%m:%d %H:%M:%S")
        except Exception as ex:
            print("ERROR: Can't load new datetime, check format?")
            print(ex)
            return False
        self.createTargetDir()
        #check for collisions
        if self.checkForCollisions() is True:
            self.setupNextInput()
            return False
        #write table entry and import file
        self.newTags = self.textbox.get()
        if self.newTags in ['\\quit', '\\exit', '\\abort']:
            self.master.quit()
            return None
        else:
            self.input_strings.append(self.newTags)
            self.currentInputIndex += 1
        taglist = self.newTags.split(' ')
        taglist.append(self.data[self.currentImageIndex]["assessment"])
        taglist.insert(0,MONTHS[int(self.month)-1])
        taglist.insert(0,self.year)
        tags = ','.join(taglist)
        try:
            #if using default import, move file from ./inbox/, otherwise copy file
            if os.path.isfile('./inbox/'+self.data[self.currentImageIndex]["filename"]):
                os.system("mv "+self.data[self.currentImageIndex]["fullpath"].replace(' ', "\ ")+" "+NUDADBDIR+self.year+'-'+self.month+'/'+self.newName)
            else:
                os.system("cp "+self.data[self.currentImageIndex]["fullpath"].replace(' ', "\ ")+" "+NUDADBDIR+self.year+'-'+self.month+'/'+self.newName)
            #Add entry to table
            with open(NUDADBTABLE, 'a') as table:
                table.write(self.newName+'\t'+'./nudaDBDir/'+self.year+'-'+self.month+'/'+'\t'+self.data[self.currentImageIndex]["datetime"].strftime("%Y-%m-%d\t%H:%M:%S")+'\t'+tags+'\n')
        except Exception as ex:
            print("copy problem!")
            print(ex)
        #setup next input file
        self.textbox.delete(0, tk.END)
        while not self.setup_next_input():
            print(self.data[self.currentImageIndex]["path"], "has been skipped!")
        return True

    def assess_all_images(self):
        for d in self.data:
            d["assessment"] = None
            d["datetime"] = None
            #Get file data
            d["fullpath"] = os.path.abspath(d["path"])
            d["filename"] = d["fullpath"].split('/')[-1]
            d["extension"] = d["filename"].split('.')[-1]
            d["dirpath"] = d["fullpath"][:-len(d["filename"])]
        #try to open all files as images
        for d in self.data:
            testOpen = None
            try:
                testOpen = Image.open(d["fullpath"])
                testTkImage = ImageTk.PhotoImage(testOpen)
                d["assessment"] = "image"
            except Exception as ex:
                print("Can't open "+d["fullpath"]+"... Not an image!")
                print(ex)
        #check the rest to see if they have known video format extensions
            if d["assessment"] is None:
                if d["extension"] in ["MP4","mp4","avi","AVI","3g2","MPG","mpg","wmv","MOV"]:
                    d["assessment"] = "video"
        #get EXIF date and time for files assessed as images
        for d in self.data:
            if d["assessment"] == "image":
                try:
                    testOpen = Image.open(d["fullpath"])
                    fullexif=testOpen._getexif()
                    d["datetime"] = datetime.datetime.strptime(fullexif[36867], "%Y:%m:%d %H:%M:%S")
                except Exception as ex:
                    print("PIL EXIF failed! Using exiftool...")
                    try:
                        exiftoolOutput = subprocess.run(['exiftool', '-CreateDate', d["fullpath"]], capture_output=True)
                        exiftoolDate = str(exiftoolOutput.stdout)[-22:-3]
                        d["datetime"] = datetime.datetime.strptime(exiftoolDate, "%Y:%m:%d %H:%M:%S")
                    except:
                        print("exiftool -CreateDate failed! Using file timestamp...")
                        print(ex)
                        try:
                            d["datetime"] = datetime.datetime.fromtimestamp(os.path.getmtime(d["fullpath"]))
                        except Exception as ex:    
                            print("No file timestamp!? Crashing...")
                            print(ex)
                            self.master.quit()
            elif d["assessment"] == "video":
                try:
                    exiftoolOutput = subprocess.run(['exiftool', '-CreateDate', d["fullpath"]], capture_output=True)
                    exiftoolDate = str(exiftoolOutput.stdout)[-22:-3]
                    d["datetime"] = datetime.datetime.strptime(exiftoolDate, "%Y:%m:%d %H:%M:%S")
                except Exception as ex:
                    print("exiftool -CreateDate failed! Using file timestamp...")
                    print(ex)
                    try:
                        d["datetime"] = datetime.datetime.fromtimestamp(os.path.getmtime(d["fullpath"]))
                    except Exception as ex:    
                        print("No file timestamp!? Crashing...")
                        print(ex)
                        self.master.quit()

    def setup_next_input(self, event=None):
        self.currentImageIndex += 1
        if self.currentImageIndex >= len(self.data):
            self.master.quit()
            print("DEBUG: ALL DONE")
            return True
        if self.data[self.currentImageIndex]["assessment"] is not None:
            self.createTargetDir()
            #check for collisions
            if self.checkForCollisions() is True:
                return False
        #fill datebox with current datetime info
        self.datebox.delete(0, tk.END)
        self.datebox.insert(0, self.data[self.currentImageIndex]["datetime"].strftime("%Y:%m:%d %H:%M:%S"))
        self.label.config(text="Importing File: "+self.data[self.currentImageIndex]["filename"])
        if self.data[self.currentImageIndex]["assessment"] == "image":
            self.currentImage = Image.open(self.data[self.currentImageIndex]["fullpath"]).resize((self.width,self.height), Image.LANCZOS)
            self.currentTkImage = ImageTk.PhotoImage(image=self.currentImage)
            self.showpanel.config(image = self.currentTkImage)
            self.frameImg.tkraise()
        elif self.data[self.currentImageIndex]["assessment"] == "video":
            self.frameVid.tkraise()
            self.vlcMedia = self.vlcInstance.media_new(self.data[self.currentImageIndex]["fullpath"])
            self.vlcPlayer.set_media(self.vlcMedia)
        else:
            os.system("mv "+self.data[self.currentImageIndex]["fullpath"].replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/")
            return False
        return True
