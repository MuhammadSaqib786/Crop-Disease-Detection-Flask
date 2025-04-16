# auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import create_connection

auth = Blueprint('auth', __name__)

# ------------------ SIGNUP ------------------
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        location = request.form.get('location', '')

        conn = create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (name, email, password_hash, location) VALUES (?, ?, ?, ?)', 
                           (name, email, generate_password_hash(password), location))
            conn.commit()
            flash("✅ Signup successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except:
            flash("❌ Email already exists. Try logging in.", "danger")
        finally:
            conn.close()

    return render_template('signup.html')

# ------------------ LOGIN ------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Invalid credentials!", "danger")

    return render_template('login.html')

# ------------------ LOGOUT ------------------
@auth.route('/logout')
def logout():
    session.clear()
    flash("👋 You’ve been logged out.", "info")
    return redirect(url_for('main.index'))
