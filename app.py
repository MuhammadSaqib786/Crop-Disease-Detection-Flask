# app.py

from flask import Flask, render_template, session, redirect, url_for, request
from werkzeug.utils import secure_filename
from auth import auth
from db import init_db, create_connection
from predict import predict_disease
from datetime import datetime
import os

# === Flask App Initialization ===
app = Flask(__name__)
app.secret_key = 'd3bfe0aa7ff3dbfe0e8354b76a2a9a7d' 

# === Register Blueprint for Authentication ===
app.register_blueprint(auth)

# === Initialize Database ===
init_db()

# === Upload Folder ===
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ INDEX (Welcome Page) ------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', name=session['name'])

# ------------------ PROFILE ------------------
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

# ------------------ NEW TEST (Image Upload + AI Prediction) ------------------
@app.route('/new-test', methods=['GET', 'POST'])
def new_test():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    prediction = None
    treatment = None
    image_filename = None

    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_filename = secure_filename(file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            file.save(image_path)

            # Call AI Model to Predict
            predicted_class, confidence, treatment = predict_disease(image_path)
            prediction = f"{predicted_class} ({confidence}% confidence)"

            # Save to Database
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tests (user_id, image_path, prediction, treatment, tested_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], image_filename, predicted_class, treatment, datetime.now()))
            conn.commit()
            conn.close()

    return render_template('new_test.html', prediction=prediction, treatment=treatment, image_filename=image_filename)

# ------------------ TEST HISTORY ------------------
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tests WHERE user_id = ? ORDER BY tested_at DESC', (session['user_id'],))
    tests = cursor.fetchall()
    conn.close()

    return render_template('history.html', tests=tests)

# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
