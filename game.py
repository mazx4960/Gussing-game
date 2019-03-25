import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)


def get_db():
    db = sqlite3.connect('game.sqlite3')
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def home():
    db = get_db()
    questions = db.execute('SELECT * FROM question').fetchall()
    db.close()
    return render_template('home.html', questions=questions)

@app.route('/view/<int:id>/')
def view(id):
    db = get_db()
    question = {}
    question_result = db.execute('SELECT * FROM question WHERE id=?',(id,)).fetchall()
    question['id'] = question_result[0][0]
    question['text'] = question_result[0][1]

    guesses = []
    for answer in db.execute('SELECT * FROM attempt WHERE question_id=?',(id,)).fetchall():
        guesses.append(answer[2])
    if guesses == []:
        question['MIN(guess)'] = None
        question['MAX(guess)'] = None
    else:
        question['MIN(guess)'] = min(guesses)
        question['MAX(guess)'] = max(guesses)
    db.close()

    return render_template('view.html', question = question)

@app.route('/error/')
def error():
    return render_template('error.html')


@app.route('/add/', methods=['POST'])
def add():
    question = request.form.get('text')
    answer = request.form.get('answer')
    if not question or not answer:
        return error()
    else:
        db = get_db()
        db.execute('INSERT INTO question (text,answer) VALUES (?, ?)' , (question, int(answer)))
        db.commit()
        db.close()
        return home()

@app.route('/delete/<int:id>/', methods=['POST'])
def delete(id):
    print(id)
    db = get_db()
    db.execute('DELETE FROM question WHERE id=?', (id,))
    db.commit()
    db.close()
    return home()

@app.route('/attempt/<int:id>/', methods=['POST'])
def attempt(id):
    guess = request.form.get('guess')
    if not guess:
        return render_template('error.html')
    else:
        db = get_db()
        db.execute('INSERT INTO attempt (question_id,guess) VALUES (?, ?)' , (id, int(guess)))
        db.commit()
        result = db.execute('SELECT * FROM question WHERE id=?',(id,)).fetchall()
        answer = result[0][2]
        return render_template('attempt.html',guess = int(guess), answer=answer)
