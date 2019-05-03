from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root1234'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# games
@app.route('/games')
def games():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get games
    result = cur.execute("SELECT * FROM games")

    games = cur.fetchall()

    if result > 0:
        return render_template('games.html', games=games)
    else:
        msg = 'No games Found'
        return render_template('games.html', msg=msg)
    # Close connection
    cur.close()


#Single game
@app.route('/game/<string:id>/')
def game(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get game
    result = cur.execute("SELECT * FROM games WHERE id = %s", [id])

    game = cur.fetchone()

    return render_template('game.html', game=game)


# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])
    usertype = StringField('usertype', [validators.Length(min=1, max=25)])


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        usertype = form.usertype.data
        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(username, password,usertype) VALUES(%s, %s, %s)", (username, password, usertype))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Show games only from the user logged in
    result = cur.execute("SELECT * FROM games WHERE username = %s", [session['username']])

    games = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', games=games)
    else:
        msg = 'No games Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# game Form Class
class GameForm(Form):
    question = StringField('question', [validators.Length(min=1, max=500)])
    choice1 = TextAreaField('choice1', [validators.Length(min=1)])
    choice2 = TextAreaField('choice2', [validators.Length(min=1)])
    choice3 = TextAreaField('choice3', [validators.Length(min=1)])
    answer = TextAreaField('answer', [validators.Length(min=1)])
# Add game
@app.route('/add_game', methods=['GET', 'POST'])
@is_logged_in
def add_game():
    form = GameForm(request.form)
    if request.method == 'POST' and form.validate():
        question = form.question.data
        choice1 = form.choice1.data
        choice2 = form.choice2.data
        choice3 = form.choice3.data
        answer = form.answer.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO games(username,question, choice1, choice2, choice3,answer) VALUES(%s, %s, %s,%s, %s, %s)",(session['username'],question,choice1,choice2,choice3,answer))

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('game Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_game.html', form=form)


# Edit game
@app.route('/edit_game/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_game(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get game by id
    result = cur.execute("SELECT * FROM games WHERE id = %s", [id])

    game = cur.fetchone()
    cur.close()
    # Get form
    if game["username"] == session['username']:

        form = GameForm(request.form)

        # Populate game form fields
        form.question.data = game['question']
        form.choice1.data = game['choice1']
        form.choice2.data = game['choice2']
        form.choice3.data = game['choice3']
        form.answer.data = game['answer']


        if request.method == 'POST':
            question = request.form['question']
            choice1 = request.form['choice1']
            choice2 = request.form['choice2']
            choice3 = request.form['choice3']
            answer = request.form['answer']
            # Create Cursor
            cur = mysql.connection.cursor()
            # Execute
            cur.execute ("UPDATE games SET question=%s, choice1=%s, choice2=%s, choice3=%s, answer=%s WHERE id=%s",(question, choice1,choice2,choice3,answer, id))
            # Commit to DB
            mysql.connection.commit()

            #Close connection
            cur.close()

            flash('Game Updated', 'success')

            return redirect(url_for('games'))
    else:
        flash('Unauthorized Access', 'warning')

        return redirect(url_for('games'))

    return render_template('edit_game.html', form=form)

# Delete game
@app.route('/delete_game/<string:id>', methods=['POST'])
@is_logged_in
def delete_game(id):
    # Create cursor
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM games WHERE id = %s", [id])
    game = cur.fetchone()

    if game["username"] == session['username']:


        # Execute
        cur.execute("DELETE FROM games WHERE id = %s", [id])

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('game Deleted', 'success')

        return redirect(url_for('dashboard'))
    else:
        flash('Unauthorized Access', 'warning')

        return redirect(url_for('dashboard'))

#check answer!
@app.route('/check_answer/<string:id>/<string:choice>', methods=['POST'])
@is_logged_in
def check_answer(id,choice):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    result = cur.execute("SELECT answer FROM games WHERE id = %s", [id])
    game = cur.fetchone()

    #Close connection
    cur.close()
    if game["answer"] == int(choice):
        flash('Correct answer', 'success')
    else:
        flash('Wrong answer', 'warning')

    return redirect(url_for('games'))




if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
