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
import importClass as imp 

if sys.argv[1] == "init":
    print("Initializing nudaDB into "+os.getcwd())
    os.system("mkdir ./nudaDBDir/")
    os.system("mkdir ./inbox/")
    os.system("mkdir ./search/")
    os.system("mkdir ./inbox/imported/")
    os.system("mkdir ./inbox/skipped/")
    os.system("mkdir ./flask/")
    installDir = os.path.join(os.path.split(os.path.realpath("/bin/nuda"))[0])+'/'
    os.system("cp -r "+installDir+"flask/* ./flask/")
    os.system("ln -s ../../nudaDBDir/ ./flask/static/nudaDBDir")
    if not os.path.exists(imp.NUDADBTABLE):
        print("Creating "+imp.NUDADBTABLE)
        with open(imp.NUDADBTABLE, 'w') as table:
            table.write("#filename\tpath\tdate\ttime\ttags\n")

if sys.argv[1] == "install":
    print("Installing nudaDB into "+os.getcwd())
    os.system("mkdir ./nudaDBDir/")
    os.system("mkdir ./inbox/")
    os.system("mkdir ./search/")
    os.system("mkdir ./inbox/imported/")
    os.system("mkdir ./inbox/skipped/")
    if not os.path.exists(imp.NUDADBTABLE):
        print("Creating "+imp.NUDADBTABLE)
        with open(imp.NUDADBTABLE, 'w') as table:
            table.write("#filename\tpath\tdate\ttime\ttags\n")
    if len(sys.argv) > 2:
        if sys.argv[2] == "-f":
            print("Forcing")
            os.system("sudo ln -sf "+os.getcwd()+"/nudaDB.py /bin/nuda")
    else:
        os.system("sudo ln -s "+os.getcwd()+"/nudaDB.py /bin/nuda")

else:
    if os.path.exists(imp.NUDADBDIR) and os.path.exists(imp.NUDADBTABLE):
        pass
    else:
        print("Current directory, "+os.getcwd()+", is not initialized as a nudaDB home directory.")
        sys.exit()


if sys.argv[1] == "tags":
    tagDict = {}
    with open(imp.NUDADBTABLE, 'r') as table:
        for line in table:
            if line[0] == '#':
                continue
            else:
                fname, path, date, time, tags = line.split('\t')
                tagList = tags.rstrip().split(',')
                print(fname, tagList)
                if "nsfw" not in tagList:
                    for tag in tagList:
                        tagDict.setdefault(tag, []).append(path+fname)
    print(tagDict)
    with open("tags.pickle","wb") as pickleFile:
        pickle.dump(tagDict, pickleFile, protocol=pickle.HIGHEST_PROTOCOL)

if sys.argv[1] == "search":
    tagList = sys.argv[2:]
    print('Searching for tag: ',tagList)
    imageList = imp.getImagesMatchingTags(tagList)
    os.system("rm "+imp.NUDADBDIR+"../search/*")
    for result in imageList:
        filename = result.split('/')[-1]
        os.system("ln "+imp.NUDADBDIR+"../"+result+" "+imp.NUDADBDIR+"../search/"+filename)
        with open(imp.NUDADBTABLE, 'r') as dbfile:
            for line in dbfile:
                if line[:len(filename)] == filename:
                    print(line.rstrip())

if sys.argv[1] == "slideshow":
    print("slideshow feature is disabled pending refactor")
#    tagList = sys.argv[2:]
#    print('Starting slideshow with tags: ',tagList)
#    imageList = imp.getImagesMatchingTags(tagList)
#
#    #initialize tk window
#    slideshow = tk.Tk()
#    slideshow.attributes('-type','dialog')
#    my_slideshow = imp.importClass(slideshow, imageList, 'show')
#    slideshow.mainloop()

if sys.argv[1] == "reset":
    try:
        value = os.environ['ALLOWNUDARESET']
    except:
        value = "False"
    if value == 'True':
        yesorno = input("Really reset the entire DB? ")
        if yesorno in ['yes', 'y', 'Y', 'Yes', 'YES']:
            print("Moving all imported files back to ./inbox/")
            os.system("mv ./inbox/imported/* ./inbox/")
            print("Moving all skipped files back to ./inbox/")
            os.system("mv ./inbox/skipped/* ./inbox/")
            print("Wiping nudaDBDir")
            os.system("rm ./nudaDBDir/*/*")
            os.system("rmdir ./nudaDBDir/*")
            print("Wiping nudaDBTable.txt")
            os.system("rm "+imp.NUDADBTABLE)
            if not os.path.exists(imp.NUDADBTABLE):
                print("Creating "+imp.NUDADBTABLE)
                with open(imp.NUDADBTABLE, 'w') as table:
                    table.write("#filename\tpath\tdate\ttime\ttags\n")
    else:
        print("nuda reset disabled!")

if sys.argv[1] == "import":
    if len(sys.argv) == 2:
        inFileNames = ['./inbox/'+f for f in os.listdir(os.getcwd()+'/inbox/') if os.path.isfile(os.getcwd()+'/inbox/'+f)]
    else:
        inFileNames = sys.argv[2:]
    importGUI = tk.Tk()
    importGUI.attributes('-type','dialog')
    my_importGUI = imp.importClass(importGUI, inFileNames)
    importGUI.mainloop()

