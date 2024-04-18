# app/utils.py
import sqlite3
from passlib.hash import pbkdf2_sha256
from streamlit import session_state

def get_connection():
    return sqlite3.connect('user_database.db')

def create_user_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def create_performance_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                user_id INTEGER,
                attempts INTEGER,
                marks INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

def create_user(username, password):
    hashed_password = pbkdf2_sha256.hash(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()

def user_exists(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        return cursor.fetchone() is not None

def verify_login(username, password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user is not None and pbkdf2_sha256.verify(password, user[2]):
            session_state.state['user_id'] = user[0]  # Assuming user_id is the first column
            session_state.state['is_logged_in'] = True
            session_state.state['username'] = username
            return True
    return False

def get():
    if 'state' not in session_state:
        session_state.state = {'username': '', 'password': '', 'is_logged_in': False}
    elif session_state.state['is_logged_in']:
        # Set user_id if the user is already logged in
        session_state.state['user_id'] = get_user_id(session_state.state['username'])
    return session_state.state

def get_user_id(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username=?', (username,))
        user_id = cursor.fetchone()
        if user_id:
            return user_id[0]
        else:
            return None