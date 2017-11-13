#!/usr/bin/python
#nudaDB

#TO-DO
#DONE	make path saved in table relative to directory holding nudaDB.py, to allow use on removable memory
#DONE	use file timestamp if no EXIF data
#DONE	for import, display image on screen and then prompt for tags
#DONE	for import, keep focus on terminal, autoclose displayed image after tags are entered
#	for import, suggest tags (autofill suggestions from previously used tags)
#	check entire db for duplicate files on import?
#	ability to search db and display images and edit tags
#	implement optparse
#	add command line option to keep file in inbox upon successful import
#DONE	allow wildcards on command line
#DONE	save previously entered tag-string history, accessible with up arrow (importing readline makes raw_input do this automatically)
#DONE	change name to nudusDB/nudaDB/nudumDB. ('nudus' is latin for simple/unadorned/bare)
#DONE	make it 'standalone' executable
#DONE	make 'install' command to add it to bin and create ./inbox/ and ./inbox/imported/ directories
#	write README
#	implement tag dictionary for searching

import hashlib
import sys, os
from PIL import Image
import subprocess
import datetime
from pyautogui import hotkey
import time
import readline

#NUDADBDIR = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBDir/'		#this gets the directory of the python script
NUDADBDIR = os.getcwd() + '/nudaDBDir/'							#this gets the current working directory
print NUDADBDIR
#NUDADBTABLE = os.path.dirname(os.path.abspath(sys.argv[0])) + '/nudaDBTable.txt'
NUDADBTABLE = os.getcwd() + '/nudaDBTable.txt'
MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def getHash(thefile):
	BLOCKSIZE = 65536
	hasher = hashlib.md5()
	with open(thefile, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
		print hasher.hexdigest()
	return hasher.hexdigest()


print sys.argv

if sys.argv[1] == "install":
	print "Installing nudaDB into "+os.getcwd()
	os.system("mkdir ./nudaDBDir/")
	os.system("mkdir ./inbox/")
	os.system("mkdir ./inbox/imported/")
	if not os.path.exists(NUDADBTABLE):
		print "Creating "+NUDADBTABLE
		with open(NUDADBTABLE, 'w') as table:
			table.write("#filename\tpath\tdate\ttime\ttags")
	if len(sys.argv) > 2:
		if sys.argv[2] == "-f":
			print "Forcing"
			os.system("sudo ln -sf "+os.getcwd()+"/nudaDB.py /bin/nuda")
		else:
			os.system("sudo ln -s "+os.getcwd()+"/nudaDB.py /bin/nuda")

else:
	if os.path.exists(NUDADBDIR) and os.path.exists(NUDADBTABLE):
		print "Ready, Go!"
	else:
		print "Current directory, "+os.getcwd+", is not an installed DumbDB home directory."
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
				print fname, tagList
				for tag in tagList:
					tagDict.setdefault(tag, []).append(fname)
	print tagDict


if sys.argv[1] == "import":
	for infile in sys.argv[2:]:
		#Get file data
		fullpath = os.path.abspath(infile)
		print fullpath
		filename = fullpath.split('/')[-1]
		print filename
		extension = filename.split('.')[-1]
		print extension
		dirpath = fullpath[:-len(filename)]
		print dirpath
		image = Image.open(fullpath)
		try:
			dateAndTime = datetime.datetime.strptime(image._getexif()[36867], "%Y:%m:%d %H:%M:%S")
		except:
			print "No EXIF data found!"
			try:
				dateAndTime = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
			except:	
				print "No file timestamp!?"
				sys.exit()
		image.thumbnail((800,800))
		image.save("./temp.JPG","JPEG")
		p = subprocess.Popen(["display","./temp.JPG"])
		time.sleep(0.1)#wait for display window to fully open
		hotkey('alt','tab')#switch focus back to terminal
		input_string = raw_input("Enter space-delimited tags: ")
		p.kill()
		print dateAndTime
		month = MONTHS[dateAndTime.month-1]
		print month
		taglist = input_string.split(' ')
		tags = ','.join(taglist)
		print tags
	
		#check for existing month directory, create if not exists
		dirContents = os.listdir(NUDADBDIR)
		print dirContents
		dirCheck = NUDADBDIR+month+str(dateAndTime.year)
		if month+str(dateAndTime.year) in dirContents:
			print dirCheck+'/'+"  exists!"
		else:
			print "Creating "+dirCheck
			os.system("mkdir "+dirCheck)
	
		#copy file     filename = last six characters of hashstring
		monthContents = os.listdir(NUDADBDIR+month+str(dateAndTime.year))
		fullHash = getHash(fullpath)
		newName = fullHash[-6:]+'.'+extension
		if newName in monthContents:
			print "COLLISION!     Skipping..."
			continue
		else:
			try:
				os.system("cp "+fullpath.replace(' ', "\ ")+" "+NUDADBDIR+month+str(dateAndTime.year)+'/'+newName)
				os.system("mv "+fullpath.replace(' ', "\ ")+" "+NUDADBDIR+"../inbox/imported/"+newName)
			except:
				print "copy/move problem!"
				continue
			#Add entry to table
			with open(NUDADBTABLE, 'a') as table:
				table.write(newName+'\t'+'./nudaDBDir/'+month+str(dateAndTime.year)+'/'+'\t'+dateAndTime.strftime("%Y-%m-%d\t%H:%M:%S")+'\t'+tags+'\n')
