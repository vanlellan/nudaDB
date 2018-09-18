#!/usr/bin/python3
#nudaDB: a minimal, command-line managed, ascii database for organizing pictures with dates and tags
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

import sys, os
import tkinter as tk
import pickle
import slideShowClass as ssc

if sys.argv[1] == "init":
	print("Initializing nudaDB into "+os.getcwd())
	os.system("mkdir ./nudaDBDir/")
	os.system("mkdir ./inbox/")
	os.system("mkdir ./search/")
	os.system("mkdir ./inbox/imported/")
	os.system("mkdir ./inbox/skipped/")
	if not os.path.exists(ssc.NUDADBTABLE):
		print("Creating "+ssc.NUDADBTABLE)
		with open(ssc.NUDADBTABLE, 'w') as table:
			table.write("#filename\tpath\tdate\ttime\ttags")

if sys.argv[1] == "install":
	print("Installing nudaDB into "+os.getcwd())
	os.system("mkdir ./nudaDBDir/")
	os.system("mkdir ./inbox/")
	os.system("mkdir ./search/")
	os.system("mkdir ./inbox/imported/")
	os.system("mkdir ./inbox/skipped/")
	if not os.path.exists(ssc.NUDADBTABLE):
		print("Creating "+ssc.NUDADBTABLE)
		with open(ssc.NUDADBTABLE, 'w') as table:
			table.write("#filename\tpath\tdate\ttime\ttags")
	if len(sys.argv) > 2:
		if sys.argv[2] == "-f":
			print("Forcing")
			os.system("sudo ln -sf "+os.getcwd()+"/nudaDB.py /bin/nuda")
		else:
			os.system("sudo ln -s "+os.getcwd()+"/nudaDB.py /bin/nuda")

else:
	if os.path.exists(ssc.NUDADBDIR) and os.path.exists(ssc.NUDADBTABLE):
		pass
	else:
		print("Current directory, "+os.getcwd()+", is not initialized as a nudaDB home directory.")
		sys.exit()


if sys.argv[1] == "tags":
	tagDict = {}
	with open(ssc.NUDADBTABLE, 'r') as table:
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
	tagList = sys.argv[2:]
	print('Searching for tag: ',tagList)
	imageList = ssc.getImagesMatchingTags(tagList)
	os.system("rm "+ssc.NUDADBDIR+"../search/*")
	for result in imageList:
		filename = result.split('/')[-1]
		os.system("ln -s "+ssc.NUDADBDIR+"../"+result+" "+ssc.NUDADBDIR+"../search/"+filename)
		with open(ssc.NUDADBTABLE, 'r') as dbfile:
			for line in dbfile:
				if line[:len(filename)] == filename:
					print(line.rstrip())

if sys.argv[1] == "slideshow":
	tagList = sys.argv[2:]
	print('Starting slideshow with tags: ',tagList)
	imageList = ssc.getImagesMatchingTags(tagList)

	#initialize tk window
	slideshow = tk.Tk()
	my_slideshow = ssc.slideShowClass(slideshow, imageList, 'show')
	slideshow.mainloop()

if sys.argv[1] == "reset":
	try:
		value = os.environ['ALLOWNUDARESET']
	except:
		print("nuda reset disabled!")
		value = "False"
	if value == 'True':
		yesorno = input("Really reset the entire DB? ")
		if yesorno in ['yes', 'y', 'Y', 'Yes', 'YES']:
			print("Moving all imported files back to ./inbox/")
			os.system("mv ./nudaDBDir/*/*.* ./inbox/")
			print("Wiping ./inbox/imported/")
			os.system("rm ./inbox/imported/*")
			print("Wiping nudaDBTable.txt")
			os.system("rm "+ssc.NUDADBTABLE)
			if not os.path.exists(ssc.NUDADBTABLE):
				print("Creating "+ssc.NUDADBTABLE)
				with open(ssc.NUDADBTABLE, 'w') as table:
					table.write("#filename\tpath\tdate\ttime\ttags\n")

if sys.argv[1] == "import":
	if len(sys.argv) == 2:
		inFileNames = ['./inbox/'+f for f in os.listdir(os.getcwd()+'/inbox/') if os.path.isfile(os.getcwd()+'/inbox/'+f)]
	else:
		inFileNames = sys.argv[2:]
	importImage = tk.Tk()
	my_importImage = ssc.slideShowClass(importImage, inFileNames, 'import')
	importImage.mainloop()

