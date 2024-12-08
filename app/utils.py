import sqlite3
from functools import wraps
from flask import session, redirect, url_for

def get_db_connection():
    conn = sqlite3.connect("instance/ffin.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
