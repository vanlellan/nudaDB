#!/usr/bin/python3
from flask import Flask, render_template
import pickle
import os
import random

def getRandomTags(aNum):
    with open("../tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
        allKeys = tagDict.keys() 
        randKeys = random.sample(allKeys, aNum)
        return randKeys

def getImagesMatchingTags(listOfTags):
    with open("../tags.pickle","rb") as pickleFile:
        tagDict = pickle.load(pickleFile)
    imagelist = []
    for tag in listOfTags:
        for result in tagDict[tag]:
            imagelist.append(result)
    return imagelist

DB_FOLDER = os.path.join('static','nudaDBDir')

app = Flask(__name__, template_folder="templates")
app.config['DB_FOLDER'] = DB_FOLDER

numImages = 8

@app.route('/')
def home():
    #dummy home page
    return "APPEND your keyword to the address (slash delimited) to begin your Search!"

@app.route('/<keyword>')
@app.route('/<keyword>/<int:page>')
def search(keyword,page=None):
    imageList = [f[12:] for f in getImagesMatchingTags(keyword.split('-'))]
    if page is None:
        page = 1
        full_filenames = [os.path.join(app.config['DB_FOLDER'], f) for f in imageList[numImages*(page-1):numImages*page]]
    else:
        full_filenames = [os.path.join("..", app.config['DB_FOLDER'], f) for f in imageList[numImages*(page-1):numImages*page]]
    print(full_filenames)
    return render_template("search.html", images = full_filenames, keyword = keyword, prevthisnext = [page-1, page, page+1], randTags = getRandomTags(10))

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')