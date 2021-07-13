import os
import configparser
from flask import Flask, Response, request, flash, redirect, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app)
path = os.getcwd()
upload_dir = os.path.join(path, 'upload')
app.config['UPLOAD_FOLDER'] = upload_dir
if not os.path.isdir(upload_dir):
    os.makedirs(upload_dir)

def file_check(filename):
    allowed_extensions = (["evtx", "txt"])
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

# base upload
@app.route("/upload", methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']

        if file.filename == "":
            return redirect(request.url)
        
        if file and file_check(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # file.save(file.filename)
        else:
            return "FAIL2"
        
        
    
    
# base landing
@app.route("/")
def index():
    return render_template('index.html')


