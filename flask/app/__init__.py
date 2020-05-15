from flask import Flask
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(app.root_path, 'downloads')
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'askldfj0932409gahzb@(#!)'

from app import routes
