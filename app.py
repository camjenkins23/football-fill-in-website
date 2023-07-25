from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import random


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to SQLite database
db = SQL("sqlite:///ffin.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():

    videos = db.execute("SELECT * FROM archive ORDER BY o DESC")

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

        for letter in query:
            if letter in ["'", '"', '/', '%', '_']:
                return render_template('sorry.html', message="""Sorry, your query was invalid as it contained one of the following characters [', ", /, %, _]""")


        # Perform search based on the selected filter
        if filter == 'title':
            videos = db.execute("SELECT * FROM archive WHERE title LIKE ? ORDER BY o", ("%" + query + "%"))
            message = "Sorry, no video was found for the title '{}'.".format(query)

        elif filter == 'guest':
            videos = db.execute("SELECT * FROM archive WHERE guests LIKE ? ORDER BY o", ("%" + query + "%"))
            message = "Sorry, no video was found for the guest '{}'.".format(query)

        elif filter == 'week':
            videos = db.execute("SELECT * FROM archive WHERE week = ? ORDER BY o", query)
            message = "Sorry, no video was found for the week '{}'.".format(query)

        if videos == []:
            return render_template("sorry.html", message=message)

        # Return the search results or render a template with the results
        return render_template('results.html', videos=videos)


@app.route('/rules', methods=['GET', 'POST'])
def rules():
    if request.method == "GET":
        return render_template('rules.html')
    elif request.method == "POST":
        counter = 0
        questions = []
        while counter < 20:
            db_question = random.randint(1, 317)
            question_data = db.execute("SELECT * FROM quiz WHERE id = ?", db_question)
            question = {
                'question': question_data[0]['question'],
                'answer_choices': [question_data[0]['answer'], question_data[0]['p1'], question_data[0]['p2'], question_data[0]['p3']],
                'number': counter,
                'db': db_question
            }
            random.shuffle(question['answer_choices'])
            questions.append(question)
            counter += 1

        return render_template('quiz.html', questions=questions)


@app.route('/quiz', methods=['POST'])
def quiz():
        answers = [value for key, value in request.form.items() if key.startswith('selected')]
        ids = request.form.getlist('question-id')
        score = 0
        counter = 0
        question_answer = []
        while counter < 20:
            user_answer = answers[counter]
            id = ids[counter]
            for letter in id:
                if letter in ["'", '"', '/', '%', '_']:
                    return render_template('sorry.html', message="""Sorry, your query was invalid as it contained one of the following characters [', ", /, %, _]""")
            correct_answer_question = db.execute("SELECT answer, question FROM quiz WHERE id = ?", id)
            if user_answer == correct_answer_question[0]['answer']:
                score += 1

            question_answer.append([correct_answer_question[0]['question'], correct_answer_question[0]['answer'], user_answer,])

            counter += 1


        return render_template('self.html', questions=question_answer, score=score)




@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        user_username = request.form.get("l-username")
        user_password = request.form.get("l-password")


        for letter in user_username:
                if letter in ["'", '"', '/', '%', '_']:
                    return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")

        for letter in user_password:
            if letter in ["'", '"', '/', '%', '_']:
                return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")


        # Ensure username was submitted
        if not user_username:
            return render_template('sorry.html',message='You must provide a username.')

        # Ensure password was submitted
        elif not user_password:
            return render_template('sorry.html',message='You must provide a password.')

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username LIKE ?", user_username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], user_password):
            return render_template('sorry.html',message='Invalid username or password')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/forum")


    elif request.method == 'GET':
        return render_template('login.html')

@app.route("/register", methods=["POST"])
def register():
    user_username = request.form.get('r-username')
    user_password = request.form.get('r-password')
    db_usernames = db.execute('SELECT username FROM users')

    if user_username == "" or user_password == "" or user_password != request.form.get('r-confirm'):
            return render_template('sorry.html', message="Username or Password Invalid. Please Try Again.")

    for letter in user_username:
            if letter in ["'", '"', '/', '%', '_']:
                return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")

    for letter in user_password:
        if letter in ["'", '"', '/', '%', '_']:
            return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")

    for username in db_usernames:
        if username['username'].upper() == user_username.upper():
            return render_template('sorry.html', message="Username Taken. Please Try Again.")

    db.execute("INSERT INTO users (username, hash) VALUES (?,?)", user_username, generate_password_hash(user_password))

    return redirect('/forum')

@app.route("/thread", methods=['GET', 'POST'])
def thread():

    if request.method == 'POST':
            diff = int(request.form.get('diff'))
            comment = request.form.get('textarea')
            post_id = request.form.get('id')

            if comment in ['']:
                return render_template('sorry.html', message="Invalid comment or reply. Please Try Again.")
            print(diff)


            if diff == 1:
                 db.execute('INSERT INTO comments (user_id, post_id, text) VALUES (?,?,?)', session['user_id'], post_id, comment)
            elif diff == 2:
                 comment_id = request.form.get('comment_id')
                 db.execute('INSERT INTO replies (user_id, post_id, comment_id, text) VALUES (?, ?, ?, ?)', session['user_id'], post_id, comment_id, comment)

    post = []
    comments = []
    id = request.args.get('id')

    db_post = db.execute('SELECT * FROM posts WHERE id = ?', id)
    db_comments = db.execute('SELECT * FROM comments WHERE post_id = ?', id)

    for item in db_post:
        post.append([item['title'], db.execute('SELECT username FROM users WHERE id = ?', item['user_id']), db.execute('SELECT COUNT(*) AS count FROM comments WHERE post_id = ?', id), item['content']])

    for item in db_comments:
         db_replies = db.execute('SELECT * FROM replies WHERE comment_id = ?', item['id'])
         replies = []
         for reply in db_replies:
             replies.append([reply['text'], db.execute('SELECT username FROM users WHERE id = ?', reply['user_id'])])

         comments.append([item['text'], db.execute('SELECT username FROM users WHERE id = ?', item['user_id']), replies, item['id']])


    return render_template('thread.html', post=post, comments=comments, id=id)





@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():

    if request.method == 'POST':
        pass

    posts = []
    db_posts = db.execute('SELECT * FROM posts')
    for post in db_posts:
        posts.append([post['title'], db.execute('SELECT username FROM users WHERE id = ?', post['user_id']), db.execute('SELECT COUNT(*) AS count FROM comments WHERE post_id = ?', post['id']), post['id']])

    username = db.execute('SELECT username FROM users WHERE id = ?', session['user_id'])

    return render_template('forum.html', posts=posts, username=username)

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

    if title == "" or content == "":
            return render_template('sorry.html', message="Please enter text to post. Please Try Again.")

    for letter in title:
            if letter in ["'", '"', '/', '%', '_']:
                return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")

    for letter in content:
        if letter in ["'", '"', '/', '%', '_']:
            return render_template('sorry.html', message="""Sorry, your username was invalid as it contained one of the following characters [', ", /, %, _]""")

    db.execute('INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)', session['user_id'], title, content)

    return redirect('/forum')


if __name__ == '__main__':
    app.run()