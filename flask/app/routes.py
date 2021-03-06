from flask import render_template
from app import app

import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file
from werkzeug.utils import secure_filename

from app import generate_calendar

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/quotes')
def quotes():
    quotes = [
                {'author': 'Andreas',
                 'body': 'Dies war keine gute Idee',
                 'date': '2020-04-14'},
            ]
    return render_template('quotes.html', title='Quotes (at least allegedly):', quotes=quotes)


@app.route('/me')
def me():
    return render_template('me.html', title='About myself')


@app.route('/about')
def about():
    return render_template('about.html', title='About myself')


@app.route('/orthoschedule', methods=['GET', 'POST'])
def orthoschedule():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No selected file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            if filename[-4:] == '.xls':
                savedfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(savedfilename)
                try:
                    icsname = generate_calendar.main(inputfilename=savedfilename,
                                                     outputpath=app.config['DOWNLOAD_FOLDER'],
                                                     doctorname=request.form['doctorname'])
                    os.remove(savedfilename)
                except:
                    os.remove(savedfilename)
                    flash('Please provide a valid .xls file')
                    return redirect(request.url)
            else:
                flash('Please provide a valid .xls file')
                return redirect(request.url)

            return redirect(url_for('download_ics', icsname=icsname))

    return render_template('orthoschedule/upload_ortho_schedule.html', title='Dienstplan Ortho')


@app.route('/downloads/<icsname>')
def download_ics(icsname):
    return send_file(app.config['DOWNLOAD_FOLDER']+'/{}'.format(icsname))
