import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for
from functools import wraps
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import random

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("ffin.db")
    conn.row_factory = sqlite3.Row  # Rows returned as dictionaries
    return conn

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    with get_db_connection() as conn:
        videos = conn.execute("SELECT * FROM archive ORDER BY o DESC").fetchall()
    return render_template('index.html', videos=videos)

@app.route('/host')
def hosts():
    return render_template('hosts.html')

@app.route('/archive', methods=['GET', 'POST'])
def archive():
    if request.method == 'GET':
        return render_template('archive.html')
    elif request.method == 'POST':
        query = request.form.get('query')
        filter = request.form.get('filter')

        if any(letter in ["'", '"', '/', '%', '_'] for letter in query):
            return render_template('sorry.html', message="Invalid characters in query.")

        with get_db_connection() as conn:
            if filter == 'title':
                videos = conn.execute("SELECT * FROM archive WHERE title LIKE ? ORDER BY o", (f"%{query}%",)).fetchall()
            elif filter == 'guest':
                videos = conn.execute("SELECT * FROM archive WHERE guests LIKE ? ORDER BY o", (f"%{query}%",)).fetchall()
            elif filter == 'week':
                videos = conn.execute("SELECT * FROM archive WHERE week = ? ORDER BY o", (query,)).fetchall()

        if not videos:
            return render_template('sorry.html', message=f"No videos found for {filter}: {query}")
        return render_template('results.html', videos=videos)

@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if request.method == "GET":
        return render_template('rules.html')
    elif request.method == "POST":
        questions = []
        with get_db_connection() as conn:
            while len(questions) < 20:
                db_question = random.randint(1, 317)
                question_data = conn.execute("SELECT * FROM quiz WHERE id = ?", (db_question,)).fetchone()
                if question_data:
                    question = {
                        'number': len(questions),  # Assign the current question index
                        'question': question_data['question'],
                        'answer_choices': [
                            question_data['answer'],
                            question_data['p1'],
                            question_data['p2'],
                            question_data['p3']
                        ],
                        'db': db_question
                    }
                    random.shuffle(question['answer_choices'])
                    questions.append(question)
        return render_template('quiz.html', questions=questions)


@app.route('/quiz', methods=['POST'])
def quiz():
    answers = [value for key, value in request.form.items() if key.startswith('selected')]
    ids = request.form.getlist('question-id')
    score = 0
    question_answer = []

    with get_db_connection() as conn:
        for user_answer, id in zip(answers, ids):
            correct_answer_question = conn.execute("SELECT answer, question FROM quiz WHERE id = ?", (id,)).fetchone()
            if correct_answer_question and user_answer == correct_answer_question['answer']:
                score += 1
            question_answer.append([
                correct_answer_question['question'],
                correct_answer_question['answer'],
                user_answer
            ])
    return render_template('self.html', questions=question_answer, score=score)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        user_username = request.form.get("l-username")
        user_password = request.form.get("l-password")

        if not user_username or not user_password:
            return render_template('sorry.html', message="Username and password are required.")

        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM users WHERE username = ?", (user_username,)).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], user_password):
            return render_template('sorry.html', message="Invalid username or password.")

        session["user_id"] = rows[0]["id"]
        return redirect("/forum")

    return render_template('login.html')

@app.route("/register", methods=["POST"])
def register():
    user_username = request.form.get('r-username')
    user_password = request.form.get('r-password')
    confirm_password = request.form.get('r-confirm')

    if not user_username or not user_password or user_password != confirm_password:
        return render_template('sorry.html', message="Invalid username or password.")

    with get_db_connection() as conn:
        existing_users = conn.execute('SELECT username FROM users').fetchall()
        if any(user['username'].upper() == user_username.upper() for user in existing_users):
            return render_template('sorry.html', message="Username already taken.")

        conn.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (user_username, generate_password_hash(user_password)))

    return redirect('/forum')

@app.route("/thread", methods=['GET', 'POST'])
def thread():
    post_id = request.args.get('id')

    with get_db_connection() as conn:
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchall()
        comments = conn.execute("SELECT * FROM comments WHERE post_id = ?", (post_id,)).fetchall()

        for comment in comments:
            replies = conn.execute("SELECT * FROM replies WHERE comment_id = ?", (comment['id'],)).fetchall()
            comment['replies'] = replies

    return render_template('thread.html', post=post, comments=comments)

@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    with get_db_connection() as conn:
        posts = conn.execute('SELECT * FROM posts').fetchall()
    return render_template('forum.html', posts=posts)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect('/login')

@app.route('/post', methods=['POST'])
@login_required
def post():
    title = request.form.get('post-title')
    content = request.form.get('post-text')

    if not title or not content:
        return render_template('sorry.html', message="Title and content are required.")

    with get_db_connection() as conn:
        conn.execute('INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)', (session['user_id'], title, content))

    return redirect('/forum')

if __name__ == '__main__':
    app.run()