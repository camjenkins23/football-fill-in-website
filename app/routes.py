from flask import render_template, session, redirect, request, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from .utils import get_db_connection, login_required
import random


def register_routes(app):
    @app.route('/')
    def index():
        """Homepage route displaying video archive."""
        with get_db_connection() as conn:
            videos = conn.execute("SELECT * FROM archive ORDER BY o DESC").fetchall()
        return render_template('index.html', videos=videos)

    @app.route('/host')
    def hosts():
        """Static page for hosts."""
        return render_template('hosts.html')
    
    @app.route('/forum')
    def forum():
        return render_template('sorry.html', message="Forum functionality is currently unavailable") 

    @app.route('/archive', methods=['GET', 'POST'])
    def archive():
        """Searchable archive page."""
        if request.method == 'GET':
            return render_template('archive.html')
        elif request.method == 'POST':
            query = request.form.get('query', '')
            filter_type = request.form.get('filter', '')

            if any(letter in ["'", '"', '/', '%', '_'] for letter in query):
                return render_template('sorry.html', message="Invalid characters in query.")

            with get_db_connection() as conn:
                sql = f"SELECT * FROM archive WHERE {filter_type} LIKE ? ORDER BY o"
                results = conn.execute(sql, (f"%{query}%",)).fetchall()

            if not results:
                return render_template('sorry.html', message=f"No results found for {filter_type}: {query}")
            return render_template('results.html', videos=results)

    @app.route('/rules', methods=['GET', 'POST'])
    def rules():
        """Generate a quiz with random questions."""
        if request.method == "GET":
            return render_template('rules.html')
        elif request.method == "POST":
            questions = []
            with get_db_connection() as conn:
                while len(questions) < 20:
                    question_id = random.randint(1, 317)
                    question_data = conn.execute("SELECT * FROM quiz WHERE id = ?", (question_id,)).fetchone()
                    if question_data:
                        question = {
                            'number': len(questions) + 1,
                            'question': question_data['question'],
                            'id': question_id,
                            'answer_choices': [
                                question_data['answer'],
                                question_data['p1'],
                                question_data['p2'],
                                question_data['p3']
                            ],
                        }
                        random.shuffle(question['answer_choices'])
                        questions.append(question)
            return render_template('quiz.html', questions=questions)

    @app.route('/quiz', methods=['POST'])
    def quiz():
        """Submit and grade the quiz."""
        answers = []
        for key, value in request.form.items():
            if (key.startswith('selected ')):
                answers.append(value)

        ids = request.form.getlist('question-id')
        score = 0
        results = []

        with get_db_connection() as conn:
            for user_answer, question_id in zip(answers, ids):
                question_data = conn.execute("SELECT * FROM quiz WHERE id = ?", (question_id,)).fetchone()
                if question_data and user_answer == question_data['answer']:
                    score += 1

                results.append({
                    'question': question_data['question'],
                    'user_answer': user_answer,
                    'correct_answer': question_data['answer'],
                })
        return render_template('self.html', score=score, results=results)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login route."""
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if not username or not password:
                flash("Username and password are required.")
                return redirect(url_for('login'))

            with get_db_connection() as conn:
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            if not user or not check_password_hash(user['hash'], password):
                flash("Invalid username or password.")
                return redirect(url_for('login'))

            session["user_id"] = user["id"]
            flash("Successfully logged in.")
            return redirect(url_for('index'))

        return render_template('login.html')

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """User registration."""
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not username or not password or password != confirm_password:
                flash("Invalid registration details.")
                return redirect(url_for('register'))

            with get_db_connection() as conn:
                existing_user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                if existing_user:
                    flash("Username already exists.")
                    return redirect(url_for('register'))

                conn.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                flash("Registration successful. Please log in.")
                return redirect(url_for('login'))

        return render_template('register.html')

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        """Logout route."""
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for('index'))