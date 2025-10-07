from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string

app = Flask(__name__)
app.secret_key = 'secret-key'

USERNAME = 'admin'
PASSWORD = '321'

def generate_password(complexity, length=None):
    if complexity.lower() == 'легкий':
        default_length = 8
        characters = string.ascii_lowercase
    elif complexity.lower() == 'средний':
        default_length = 12
        characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
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

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    password = None
    if request.method == 'POST':
        complexity = request.form.get('complexity')
        length_input = request.form.get('length')

        if not complexity:
            password = "Пожалуйста, выберите уровень сложности."
        else:
            password = generate_password(complexity, length_input)

    return render_template('index.html', password=password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
