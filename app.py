from flask import Flask, render_template, request, jsonify, redirect
from textblob import TextBlob
import sqlite3
from datetime import datetime


# CREATE FLASK APPLICATION
app = Flask(__name__)



# -----------------------------
# DATABASE SETUP
# -----------------------------

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry TEXT,
            mood TEXT,
            date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HOME PAGE
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# CHATBOT PAGE
# -----------------------------

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# -----------------------------
# CHATBOT RESPONSE
# -----------------------------


@app.route('/get_response', methods=['POST'])
def get_response():

    user_message = request.json['message'].lower()

    if "sad" in user_message or "depressed" in user_message:
        response = "I'm really sorry you're feeling this way. Please remember that difficult emotions are temporary. Try talking to someone you trust and take small breaks for yourself."

    elif "stress" in user_message or "anxiety" in user_message:
        response = "Stress can feel overwhelming sometimes. Try deep breathing exercises, relaxing music, and focusing on one task at a time."

    elif "lonely" in user_message:
        response = "You are not alone. Reaching out to friends, family, or engaging in activities you enjoy may help you feel more connected."

    elif "happy" in user_message or "good" in user_message:
        response = "That’s wonderful to hear! Keep doing things that bring positivity and peace into your life."

    elif "angry" in user_message:
        response = "Take a moment to pause and breathe slowly. Writing your thoughts in the journal may help release some tension."

    else:
        response = "Thank you for sharing your feelings. Remember to take care of yourself and give yourself time to heal and grow."

    return jsonify({
        "response": response
    })


# -----------------------------
# JOURNAL PAGE
# -----------------------------

@app.route('/journal')
def journal():
    return render_template('journal.html')

# -----------------------------
# SAVE JOURNAL ENTRY
# -----------------------------

@app.route('/save_journal', methods=['POST'])
def save_journal():

    entry = request.form['entry']

    analysis = TextBlob(entry)
    polarity = analysis.sentiment.polarity

    if polarity < 0:
        mood = "Negative"

    elif polarity == 0:
        mood = "Neutral"

    else:
        mood = "Positive"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO journal (entry, mood, date) VALUES (?, ?, ?)',
        (entry, mood, str(datetime.now()))
    )

    conn.commit()
    conn.close()

    return "Journal Saved Successfully"

# -----------------------------
# BREATHING PAGE
# -----------------------------

@app.route('/breathing')
def breathing():
    return render_template('breathing.html')

# -----------------------------
# MUSIC PAGE
# -----------------------------

@app.route('/music')
def music():
    return render_template('music.html')

# -----------------------------
# RUN APPLICATION
# -----------------------------

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT mood, COUNT(*) FROM journal GROUP BY mood'
    )

    data = cursor.fetchall()

    conn.close()

    moods = []
    counts = []

    for row in data:
        moods.append(row[0])
        counts.append(row[1])

    return render_template(
        'dashboard.html',
        moods=moods,
        counts=counts
    )

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect('/')

        else:
            return "Invalid Credentials"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

