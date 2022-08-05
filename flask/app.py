#!/usr/bin/python3
from flask import Flask, render_template
import pickle
import os
import random

def getRandomTags(aNum):
    with open("../tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
        allKeys = tagDict.keys() 
        randKeys = random.sample(allKeys, min(aNum,len(allKeys)))
        return randKeys

def getImagesMatchingAnyTags(listOfTags):
    with open("../tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
    aImageList = []
    for tag in listOfTags:
        for result in tagDict[tag]:
            ext = result.split('.')[-1]
            if result in tagDict['image']:
                aImageList.append((result,'image',ext))
            elif result in tagDict['video']:
                aImageList.append((result,'video',ext))
            else:
                aImageList.append((result,'other',ext))
    return aImageList

def getFilesMatchingAllTags(listOfTags):
    with open("../tags.pickle","rb") as pickleFile:
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
    for result in aFileList:
        ext = result.split('.')[-1]
        if result in tagDict['image']:
            outputList.append((result,'image',ext))
        elif result in tagDict['video']:
            outputList.append((result,'video',ext))
        else:
            outputlist.append((result,'other',ext))
    return outputList

DB_FOLDER = os.path.join('static','nudaDBDir')

app = Flask(__name__, template_folder="templates")
app.config['DB_FOLDER'] = DB_FOLDER

numImages = 9

@app.route('/')
def home():
    #dummy home page
    return "APPEND your keywords to the address (dash delimited) to begin your Search! e.g. www.hostname.net/birthday-party to search for 'birthday' AND 'party'."

@app.route('/<keyword>')
@app.route('/<keyword>/<int:page>')
def search(keyword,page=None):
    imageList = [(f[0][12:],f[1],f[2]) for f in getFilesMatchingAllTags(keyword.split('-'))]
    if page is None:
        page = 1
        full_filenames = [(os.path.join(app.config['DB_FOLDER'], f[0]),f[1],f[2]) for f in imageList[numImages*(page-1):numImages*page]]
    else:
        full_filenames = [(os.path.join("..", app.config['DB_FOLDER'], f[0]),f[1],f[2]) for f in imageList[numImages*(page-1):numImages*page]]
    print(full_filenames)
    return render_template("search.html", images = full_filenames, keyword = keyword, prevthisnext = [page-1, page, page+1], randTags = getRandomTags(10))

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')
