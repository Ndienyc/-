from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

USERS_FILE = 'users.txt'
LOG_FILE = 'logs.txt'


def log_action(action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {action}\n")


def load_users():
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        username, password = parts[0], parts[1]
                        role = parts[2] if len(parts) > 2 else 'user'
                        users.append({'username': username, 'password': password, 'role': role})
    return users


def add_user(username, password, role='user'):
    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username},{password},{role}\n")


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'

        users = load_users()
        if any(u['username'] == username for u in users):
            flash('Это имя пользователя уже занято', 'error')
            log_action(f"Пользователь {username} попытался зарегистрироваться, но имя занято.")
        else:
            add_user(username, password, role)
            flash('Регистрация прошла успешно! Войдите в систему.', 'success')
            log_action(f"Пользователь {username} зарегистрирован.")
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        user_found = False
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')
                flash(f'Добро пожаловать, {username}!', 'success')
                log_action(f"Пользователь {username} вошел в систему.")
                user_found = True
                return redirect(url_for('index'))
        if not user_found:
            flash('Неверное имя пользователя или пароль', 'error')
            log_action(f"Неуспешная попытка входа: {username}")

    return render_template('login.html')


# Выход
@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    flash('Вы вышли из системы', 'info')
    if username:
        log_action(f"Пользователь {username} вышел.")
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    password = None
    if request.method == 'POST':
        complexity = request.form.get('complexity')
        length_input = request.form.get('length')
        if not complexity:
            flash('Пожалуйста, выберите уровень сложности', 'error')
        else:
            password = generate_password_func(complexity, length_input)
            log_action(f"{session['username']} сгенерировал пароль: {password}")
    return render_template('index.html', password=password)


@app.route('/admin/logs')
@login_required
def admin_logs():
    if session.get('role') != 'admin':
        flash('У вас нет прав для доступа к этой странице.', 'error')
        return redirect(url_for('index'))

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = f.readlines()

    return render_template('admin_logs.html', logs=logs)


def generate_password_func(complexity, length=None):
    if complexity.lower() == 'легкий':
        default_length = 8
        characters = string.ascii_lowercase
    elif complexity.lower() == 'средний':
        default_length = 12
        characters = string.ascii_letters + string.digits
    elif complexity.lower() == 'сложный':
        default_length = 16
        characters = string.ascii_letters + string.digits + string.punctuation
    elif complexity.lower() == 'очень сложный':
        default_length = 20
        characters = string.ascii_letters + string.digits + string.punctuation
    else:
        return "Неверный уровень сложности. Доступны: Легкий, Средний, Сложный, Очень Сложный."

    if length is not None:
        try:
            length = int(length)
            if length < 4 or length > 128:
                return "Длина пароля должна быть от 4 до 128 символов."
        except ValueError:
            return "Некорректное значение длины."
    else:
        length = default_length

    return ''.join(random.choice(characters) for _ in range(length))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=777)
