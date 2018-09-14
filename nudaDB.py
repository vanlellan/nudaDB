#!/usr/bin/python3
#nudaDB: a minimal, command-line managed, ascii database for organizing pictures with dates and tags
#Copyright 2017 Randall Evan McClellan

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
import sys, os
import tkinter as tk
from PIL import Image, ImageFile, ImageTk
ImageFile.LOAD_TRUNCATED_IMAGES = True
#import subprocess
import datetime
#from pyautogui import hotkey
import time
#import readline		#modifies behavior of raw_input
import pickle

#NUDADBDIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBDir/'		#this gets the directory of the python script
NUDADBDIR = os.getcwd() + '/nudaDBDir/'							#this gets the current working directory
#print NUDADBDIR
#NUDADBTABLE = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBTable.txt'
NUDADBTABLE = os.getcwd() + '/nudaDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

input_string = ''

def getHash(thefile):
	BLOCKSIZE = 65536
	hasher = hashlib.md5()
	with open(thefile, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
		print(hasher.hexdigest())
	return hasher.hexdigest()

def send_text(event):
	newText = textbox.get()
	if newText in ['\\quit', '\\exit', '\\abort']:
		popup.destroy()
	else:
		global input_string 
		input_string = newText
		popup.destroy()

#print sys.argv

if sys.argv[1] == "init":
	print("Initializing nudaDB into "+os.getcwd())
	os.system("mkdir ./nudaDBDir/")
	os.system("mkdir ./inbox/")
	os.system("mkdir ./search/")
	os.system("mkdir ./inbox/imported/")
	os.system("mkdir ./inbox/skipped/")
	if not os.path.exists(NUDADBTABLE):
		print("Creating "+NUDADBTABLE)
		with open(NUDADBTABLE, 'w') as table:
			table.write("#filename\tpath\tdate\ttime\ttags")

if sys.argv[1] == "install":
	print("Installing nudaDB into "+os.getcwd())
	os.system("mkdir ./nudaDBDir/")
	os.system("mkdir ./inbox/")
	os.system("mkdir ./search/")
	os.system("mkdir ./inbox/imported/")
	os.system("mkdir ./inbox/skipped/")
	if not os.path.exists(NUDADBTABLE):
		print("Creating "+NUDADBTABLE)
		with open(NUDADBTABLE, 'w') as table:
			table.write("#filename\tpath\tdate\ttime\ttags")
	if len(sys.argv) > 2:
		if sys.argv[2] == "-f":
			print("Forcing")
			os.system("sudo ln -sf "+os.getcwd()+"/nudaDB.py /bin/nuda")
		else:
			os.system("sudo ln -s "+os.getcwd()+"/nudaDB.py /bin/nuda")

else:
	if os.path.exists(NUDADBDIR) and os.path.exists(NUDADBTABLE):
		pass
	else:
		print("Current directory, "+os.getcwd()+", is not initialized as a nudaDB home directory.")
		sys.exit()


if sys.argv[1] == "tags":
	tagDict = {}
	with open(NUDADBTABLE, 'r') as table:
		for line in table:
			if line[0] == '#':
				continue
			else:
				fname, path, date, time, tags = line.split('\t')
				tagList = tags.rstrip().split(',')
				print(fname, tagList)
				for tag in tagList:
					tagDict.setdefault(tag, []).append(path+fname)
	print(tagDict)
	with open("tags.pickle","wb") as pickleFile:
		pickle.dump(tagDict, pickleFile, protocol=pickle.HIGHEST_PROTOCOL)

if sys.argv[1] == "search":
	with open("tags.pickle","rb") as pickleFile:
		tagDict = pickle.load(pickleFile)
#	print tagDict[sys.argv[2]]
	os.system("rm "+NUDADBDIR+"../search/*")
	for result in tagDict[sys.argv[2]]:
		filename = result.split('/')[-1]
		os.system("ln -s "+NUDADBDIR+"../"+result+" "+NUDADBDIR+"../search/"+filename)
		with open(NUDADBTABLE, 'r') as dbfile:
			for line in dbfile:
				if line[:len(filename)] == filename:
					print(line.rstrip())

if sys.argv[1] == "reset":
	yesorno = input("Really reset the entire DB? ")
	if yesorno in ['yes', 'y', 'Y', 'Yes', 'YES']:
		print("Moving all imported files back to ./inbox/")
		os.system("mv ./nudaDBDir/*/*.* ./inbox/")
		print("Wiping ./inbox/imported/")
		os.system("rm ./inbox/imported/*")
		print("Wiping nudaDBTable.txt")
		os.system("rm "+NUDADBTABLE)
		if not os.path.exists(NUDADBTABLE):
			print("Creating "+NUDADBTABLE)
			with open(NUDADBTABLE, 'w') as table:
				table.write("#filename\tpath\tdate\ttime\ttags")
		

#if sys.argv[1] == "edit":
#	readline.set_startup_hook(lambda: readline.insert_text("poop"))
#	try:
#		global input_string
#		input_string = input("Enter space-delimited tags: ")
#		print("input string = ", input_string)
#	finally:
#		print("test done!")
#	#display image
#	#load existing tag string into input memory
#	#save edited tag string to Table

if sys.argv[1] == "import":
	print("len(sys.argv)", len(sys.argv))
	if len(sys.argv) == 2:
		inFileNames = ['./inbox/'+f for f in os.listdir(os.getcwd()+'/inbox/') if os.path.isfile(os.getcwd()+'/inbox/'+f)]
	else:
		inFileName = sys.argv[2:]
	print(inFileNames)
	for infile in inFileNames:
		#Get file data
		fullpath = os.path.abspath(infile)
		print(fullpath)
		filename = fullpath.split('/')[-1]
		print(filename)
		extension = filename.split('.')[-1]
		print(extension)
		dirpath = fullpath[:-len(filename)]
		print(dirpath)
		image = Image.open(fullpath)
		try:
			dateAndTime = datetime.datetime.strptime(image._getexif()[36867], "%Y:%m:%d %H:%M:%S")
		except:
			print("No EXIF data found!")
			try:
				dateAndTime = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
			except:	
				print("No file timestamp!?")
				sys.exit()
	
		print(dateAndTime)
		month = MONTHS[dateAndTime.month-1]
		print(month)

		#check for existing month directory, create if not exists
		dirContents = os.listdir(NUDADBDIR)
		print(dirContents)
		dirCheck = NUDADBDIR+month+str(dateAndTime.year)
		if month+str(dateAndTime.year) in dirContents:
			print(dirCheck+'/'+"  exists!")
		else:
			print("Creating "+dirCheck)
			os.system("mkdir "+dirCheck)
	
		#copy file     filename = last six characters of hashstring
		monthContents = os.listdir(NUDADBDIR+month+str(dateAndTime.year))
		fullHash = getHash(fullpath)
		newName = fullHash[-6:]+'.'+extension
		if newName in monthContents:
			print("COLLISION!     Skipping...")
			os.system("mv "+fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/skipped/"+newName)
			continue
		else:
			image.thumbnail((800,800))
			image.save("./temp.JPG","JPEG")

			#initialize tk window
			popup = tk.Tk()
			popup.title("Enter space-delimited tags")
			popup.geometry("800x900")
			popup.configure(background='grey')

			#set up tk window FIXME THIS ALL SHOULD GO IN A CLASS
			img = ImageTk.PhotoImage(Image.open('./temp.JPG'))

			impanel = tk.Label(popup, image = img)
			impanel.pack(side='top', fill='both', expand='yes')

			textbox = tk.Entry(popup)
			textbox.focus()
			textbox.bind("<Return>", send_text)
			textbox.pack(side='bottom', fill='x', expand=True)
			#global input_string 
			input_string = ''

			popup.mainloop()
			print("input_string = ", input_string)

		#	p = subprocess.Popen(["display","./temp.JPG"])
		#	time.sleep(0.2)#wait for display window to fully open
		#	hotkey('alt','tab')#switch focus back to terminal
		#	try:
		#		input_string = input("Enter space-delimited tags: ")
		#		p.kill()
		#	except KeyboardInterrupt:
		#		print("\nAborting import...")
		#		p.kill()
		#		sys.exit()
			taglist = input_string.split(' ')
			tags = ','.join(taglist)
			print('tags: ', tags)
			try:
				os.system("cp "+fullpath.replace(' ', "\ ")+" "+NUDADBDIR+month+str(dateAndTime.year)+'/'+newName)
			except:
				print("copy problem!")
				continue
			#Add entry to table
			with open(NUDADBTABLE, 'a') as table:
				table.write(newName+'\t'+'./nudaDBDir/'+month+str(dateAndTime.year)+'/'+'\t'+dateAndTime.strftime("%Y-%m-%d\t%H:%M:%S")+'\t'+tags+'\n')
			#if using default import, move file from ./inbox/ to ./inbox/imported/
			if len(sys.argv) == 2:
				os.system("mv "+fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/imported/"+newName)
