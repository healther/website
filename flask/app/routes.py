from flask import render_template
from app import app

import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file
# from werkzeug.utils import secure_filename

from app import generate_calendar

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    quotes = [
            {'author': 'Andreas',
             'body': 'Dies war keine gute Idee',
             'time': '2020-04-14'},
            ]
    return render_template('index.html', title='Home', quotes=quotes)


@app.route('/doroschedule', methods=['GET', 'POST'])
def doroschedule():
    # TODO: sanitize input and clean up xls and ics
    # TODO: Add logging?
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            icsname = generate_calendar.main(filename='uploads/{}'.format(file.filename),
                                             doctorname=request.form['doctorname'])
            return redirect(url_for('download_ics', icsname=icsname))

    return render_template('upload.html')


@app.route('/download/<icsname>')
def download_ics(icsname):
    return send_file('../downloads/{}'.format(icsname))
