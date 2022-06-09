#!/usr/bin/python3
from flask import Flask, render_template
import pickle
import os

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

numImages = 5

@app.route('/')
def home():
    #dummy home page
    return "Hello Search!"

@app.route('/<keyword>')
@app.route('/<keyword>/<int:page>')
def search(keyword,page=None):
    print("keyword = ", keyword)
    print("page = ", page)
    imageList = [f.strip("./nudaDBDir") for f in getImagesMatchingTags(keyword.split('-'))]
    if page is None:
        page = 1
        full_filenames = [os.path.join(app.config['DB_FOLDER'], f) for f in imageList[numImages*(page-1):numImages*page]]
    else:
        full_filenames = [os.path.join("..", app.config['DB_FOLDER'], f) for f in imageList[numImages*(page-1):numImages*page]]
    #get first filenames
    #filenames = [f for f in os.listdir(SEARCH_FOLDER) if os.path.isfile(os.path.join(SEARCH_FOLDER, f))][:3]
    #full_filenames = [os.path.join(app.config['DUMMY_FOLDER'], f) for f in filenames]
    #return render_template("three-image.html", image0 = full_filenames[0], image1 = full_filenames[1], image2 = full_filenames[2])
    #return "The keyword is: "+keyword+"/n/n The images are: "+'\n'.join(imageList)
    print("full_filenames = ", full_filenames)
    return render_template("search.html", images = full_filenames)

if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')
