import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import fastai
import torch
from fastai.vision.all import *

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = load_learner('model_export.pkl')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('prediction', filename=filename))
    return '''
    <!doctype html>
    <title>Upload image to classify disease</title>
    <h1>Upload image to classify disease</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=classify>
    </form>
    '''

@app.route('/prediction/<filename>')
def prediction(filename):
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    prediction = model.predict(full_filename)
    confidence = torch.max(prediction[2]).item()
    xxx = f'../static/{filename}'
    return render_template("uploads.html", filename = xxx, confidence = confidence, label = prediction[0]) 

