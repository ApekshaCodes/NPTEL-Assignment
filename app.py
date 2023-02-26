from flask import Flask, flash,redirect,url_for, render_template, request, send_file
from flask_mail import Message, Mail
from flask_mysqldb import MySQL
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import hashlib
import uuid
import io
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
import secrets
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mail import Mail,Message
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from mutagen.easyid3 import EasyID3
import os
from bs4 import BeautifulSoup
import requests
import sys
from flask_wtf.csrf import CSRFProtect

from itsdangerous import URLSafeTimedSerializer,SignatureExpired

app = Flask(__name__)
name1=""
usernname1=""
email1=""
password1=""
username2=""
app.config['SECRET_KEY'] = 'secret21'

# Create a connection to the MySQL database
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="music_streaming"
)

app.config.from_pyfile('config.cfg')
mail=Mail(app)


s=URLSafeTimedSerializer('secret123')

mysql=MySQL(app)
        
# Create a cursor object to interact with the database
cursor = db.cursor()

UPLOAD_FOLDER = 'upload_songs'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    # Get the query parameter from the user
    query = request.args.get('q')

    # Write a SQL query to search for the song
    sql = "SELECT * FROM songs_list WHERE img LIKE %s OR song_name LIKE %s OR album LIKE %s OR contributing_artist LIKE %s"
    val = (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")

    # Execute the SQL query and fetch the results
    mycursor = db.cursor()
    mycursor.execute(sql, val)
    results = mycursor.fetchall()

    # Render the results to a template
    return render_template('search.html', results=results)

UPLOAD_FOLDER = 'upload_songs'

mp3file =''

@app.route('/allsongs', methods=['GET', 'POST'])
def allsongs():
    if request.method == 'POST':
        # Get the uploaded file from the form data
        song_file = request.files['song-file']

        # Save the uploaded file to the upload folder
        file_path = os.path.join(UPLOAD_FOLDER, song_file.filename)
        song_file.save(file_path)

        # Get the metadata from the form data
        song_name = request.form['song-name']
        song_artist = request.form['song-artist']
        song_album = request.form['song-album']

        # Insert the file path and metadata into the MySQL database
        sql = "INSERT INTO songs_list (path, song_name, contributing_artist, album) VALUES (%s, %s, %s, %s)"
        values = (file_path, song_name, song_artist, song_album)
        cursor.execute(sql, values)
        db.commit()

        flash('File uploaded successfully!')
        
    return render_template('allsongs.html')

@app.route('/button_click')
def button_click():
    return redirect(url_for('songs'))

@app.route('/songs', methods=['GET', 'POST'])
def songs():
    
           cursor = db.cursor()
           cursor.execute("SELECT * FROM songs_list")
           songs = cursor.fetchall()
           return render_template('songs.html', songs=songs)

@app.route('/song/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM songs_list WHERE id = %s", (song_id,))
    db.commit()
    flash('Song deleted successfully', 'success')
    return redirect(url_for('songs'))

@app.route('/play_song/<int:song_id>', methods=['GET'])
def play_song(song_id):
    # Retrieve song from database
    cursor = db.cursor()
    cursor.execute("SELECT song_name, path FROM songs_list WHERE id = %s", (song_id,))
    mp3data = cursor.fetchone()[1].encode('utf-8')
    return send_file(io.BytesIO(mp3data), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)

