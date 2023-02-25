from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'my_music'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Define routes

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user input from form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        # Hash password with bcrypt
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # Insert user data into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        # Redirect to login page
        return redirect(url_for('login'))
    # If GET request, show register form
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user input from form
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        # Get user data from MySQL database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            # Check if password matches hashed password in database
            if bcrypt.checkpw(password, user['password'].encode('utf-8')):
                # Store user data in session and redirect to home page
                session['user'] = user
                return redirect(url_for('home'))
        # If email or password is incorrect, show error message
        error = 'Invalid email or password'
        return render_template('login.html', error=error)
    # If GET request, show login form
    return render_template('login.html')

# Home page
@app.route('/')
def home():
    # If user is not logged in, redirect to login page
    if 'user' not in session:
        return redirect(url_for('login'))
    # Show home page with search form
    return render_template('home.html')

# Search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    # If user is not logged in, redirect to login page
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Get search term from form
        search_term = request.form['search-term']
        # Get songs matching search term from MySQL database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM songs WHERE title LIKE %s OR artist LIKE %s OR album LIKE %s", ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
        songs = cur.fetchall()
        cur.close()
        # Show search results page with matching songs
        return render_template('search.html', songs=songs)
        # If GET request, show search form
    return render_template('search.html')

# Create playlist page
@app.route('/createplaylist', methods=['GET', 'POST'])
def createplaylist():
    # If user is not logged in, redirect to login page
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Get playlist name and songs from form
        playlist_name = request.form['playlist-name']
        songs = request.form.getlist('songs')
        # Get user ID from session
        user_id = session['user']['id']
        # Insert playlist data into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO playlists (name, user_id) VALUES (%s, %s)", (playlist_name, user_id))
        playlist_id = cur.lastrowid
        for song_id in songs:
            cur.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)", (playlist_id, song_id))
        mysql.connection.commit()
        cur.close()
        # Redirect to view all playlists page
        return redirect(url_for('view-playlists'))
    # If GET request, show create playlist form
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM songs")
    songs = cur.fetchall()
    cur.close()
    return render_template('createplaylist.html', songs=songs)

# View all songs page
@app.route('/view-songs')
def allsongs():
    # If user is not logged in, redirect to login page
    if 'user' not in session:
        return redirect(url_for('login'))
    # Get all songs from MySQL database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM songs")
    songs = cur.fetchall()
    cur.close()
    # Show view all songs page with all songs
    return render_template('allsongs.html', songs=songs)

# View all playlists page
@app.route('/view-playlists')
def view_playlists():
    # If user is not logged in, redirect to login page
    if 'user' not in session:
        return redirect(url_for('login'))
    # Get user ID from session
    user_id = session['user']['id']
    # Get all playlists for user from MySQL database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM playlists WHERE user_id = %s", (user_id,))
    playlists = cur.fetchall()
    for playlist in playlists:
        # Get songs for each playlist from MySQL database
        cur.execute("SELECT s.* FROM songs s JOIN playlist_songs ps ON s.id = ps.song_id WHERE ps.playlist_id = %s", (playlist['id'],))
        playlist['songs'] = cur.fetchall()
    cur.close()
    # Show view all playlists page with all playlists for user
    return render_template('view-playlists.html', playlists=playlists)

# Logout page
@app.route('/logout')
def logout():
    # Remove user data from session and redirect to login page
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

   
