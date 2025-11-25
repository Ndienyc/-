from flask import Flask, render_template, request, redirect, url_for, session, flash
import secrets, string
from functools import wraps
from database import init_db, register_user, verify_user, save_password, get_user_passwords, get_all_users, get_all_passwords

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
ADMIN_USERNAME = 'admin'

init_db()

def generate_password(length=12, use_uppercase=True, use_lowercase=True, use_digits=True, use_special=True):
    chars = ''
    if use_uppercase: chars += string.ascii_uppercase
    if use_lowercase: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += string.punctuation
    return ''.join(secrets.choice(chars or string.ascii_letters + string.digits) for _ in range(length))

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Войдите в систему', 'warning')
            return redirect(url_for('login'))
        if session['username'] != ADMIN_USERNAME:
            flash('Только для администраторов', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapper

def is_admin():
    return 'username' in session and session['username'] == ADMIN_USERNAME

@app.route('/')
def index():
    return redirect(url_for('dashboard' if 'username' in session else 'login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password, confirm = request.form.get('username'), request.form.get('password'), request.form.get('confirm_password')
        if not username or not password:
            flash('Заполните все поля', 'danger')
        elif password != confirm:
            flash('Пароли не совпадают', 'danger')
        elif register_user(username, password):
            flash('Регистрация успешна!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь уже существует', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form.get('username'), request.form.get('password')
        if verify_user(username, password):
            session['username'] = username
            flash('Вход выполнен!', 'success')
            return redirect(url_for('dashboard'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        service = request.form.get('service')
        length = int(request.form.get('length', 12))
        use_upper, use_lower, use_digits, use_special = 'uppercase' in request.form, 'lowercase' in request.form, 'digits' in request.form, 'special' in request.form
        
        complexity = ','.join(filter(None, [
            'A-Z' if use_upper else None,
            'a-z' if use_lower else None,
            '0-9' if use_digits else None,
            '!@#' if use_special else None
        ])) or 'Нет'
        
        password = generate_password(length, use_upper, use_lower, use_digits, use_special)
        save_password(session['username'], service, password, length, complexity)
        flash(f'Пароль для {service} создан!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard.html', passwords=get_user_passwords(session['username']), username=session['username'], is_admin=is_admin())

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html', users=get_all_users(), all_passwords=get_all_passwords(), username=session['username'])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
