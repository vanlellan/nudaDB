
from flask import Flask, render_template
import os

SEARCH_FOLDER = os.path.join('static','search')

app = Flask(__name__)
app.config['DUMMY_FOLDER'] = SEARCH_FOLDER

@app.route('/')
@app.route('/templates')
def show_index():
    #get first filename
    filenames = [f for f in os.listdir(SEARCH_FOLDER) if os.path.isfile(os.path.join(SEARCH_FOLDER, f))][:3]
    full_filenames = [os.path.join(app.config['DUMMY_FOLDER'], f) for f in filenames]
    return render_template("three-image.html", image0 = full_filenames[0], image1 = full_filenames[1], image2 = full_filenames[2])

app.run(debug=True, port=8080, host='0.0.0.0')
