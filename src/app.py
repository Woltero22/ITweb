from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, session
from werkzeug.utils import secure_filename
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(id=user[0], username=user[1], password=user[2])
        return None
    
base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, '../templates'), static_folder=os.path.join(base_dir, '../static'))
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, '../files')
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            filepath TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            user_id = c.lastrowid  # Pobranie ID nowo zarejestrowanego użytkownika
            user = User(id=user_id, username=username, password=hashed_password)
            login_user(user)  # Logowanie użytkownika
            flash('Registration successful! You are now logged in.')
            return redirect(url_for('str_start'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(id=user[0], username=user[1], password=user[2])
            login_user(user_obj)
            flash('Login successful!')
            return redirect(url_for('str_start'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/str_start')
def str_start():
    return render_template('str_start.html') 

@app.route('/analiza')
def analiza():
    return render_template('analiza.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/onas')
def onas():
    return render_template('onas.html')

@app.route('/kontakt')
def kontakt():
    return render_template('kontakt.html')

@app.route('/equalizer', methods=['GET', 'POST'])
@login_required
def equalizer():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('equalizer'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('equalizer'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute('INSERT INTO files (filename, filepath, user_id) VALUES (?, ?, ?)', 
                          (filename, filepath, current_user.id))
                conn.commit()
                flash('File successfully uploaded')
            except sqlite3.Error as e:
                flash(f'Database error: {e}')
            finally:
                conn.close()
        else:
            flash('Allowed file types are mp3')
            return redirect(url_for('equalizer'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT filename FROM files WHERE user_id = ?', (current_user.id,))
    files = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template('equalizer.html', files=files)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT filepath FROM files WHERE filename = ? AND user_id = ?', (filename, current_user.id))
    file = c.fetchone()
    conn.close()
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        flash('File not found or you do not have access to it.')
        return redirect(url_for('equalizer'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(debug=True)



