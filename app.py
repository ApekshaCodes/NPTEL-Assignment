from flask import Flask, flash,redirect,url_for, render_template, request
from flask_mail import Message, Mail
from flask_mysqldb import MySQL
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import hashlib
import uuid
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
csrf = CSRFProtect(app)

s=URLSafeTimedSerializer('secret123')

mysql=MySQL(app)
        
# Create a cursor object to interact with the database
cursor = db.cursor()

app.config['UPLOAD_FOLDER'] = 'upload_songs'

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

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        # Get the form data from the user
        playlist_name = request.form['playlist_name']
        playlist_desc = request.form['playlist_desc']
        playlist_img = request.files['playlist_img']

        # Save the image file to disk
        img_path = f"img/{playlist_img.filename}"
        playlist_img.save(img_path)

        # Write a SQL query to insert the playlist into the database
        sql = "INSERT INTO playlists (playlist_name, playlist_desc, playlist_img) VALUES (%s, %s, %s)"
        val = (playlist_name, playlist_desc, img_path)

        # Execute the SQL query to insert the playlist into the database
        mycursor = db.cursor()
        mycursor.execute(sql, val)
        db.commit()

        flash('Playlist Created Successfully!')

        # Redirect to the same page to clear the form
        return redirect(url_for('create_playlist'))

    # Retrieve the existing playlists from the database
    mycursor = db.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM playlists")
    playlists = mycursor.fetchall()
    
   # Render the create playlist form with the existing playlists
    return render_template('create_playlist.html', playlists=playlists)

@app.route('/delete/<playlist>', methods=['POST'], endpoint='delete_playlist')
def delete_playlist(playlist):
    playlist_name = request.args.get('playlist_name')
    cursor = db.cursor()
    sql = "DELETE FROM playlists WHERE name = %s"
    val = (playlist_name,)
    cursor.execute(sql,val)
    db.commit()
    flash('Playlist deleted successfully', 'success')
    url_for('delete_playlist', playlist_name=playlist_name)


 

UPLOAD_FOLDER = 'upload_songs'

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


cursor.close()

if __name__ == '__main__':
    app.run(debug=True)

