import sqlite3

DB_FILE = 'passwords.db'

def init_db():
    import os
    print("✅ База подключена" if os.path.exists(DB_FILE) else "❌ База не найдена")

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    result = conn.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password)).fetchone()
    conn.close()
    return result is not None

def save_password(username, service, password, length, complexity):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('INSERT INTO passwords (username, service, password, length, complexity) VALUES (?, ?, ?, ?, ?)', 
                 (username, service, password, length, complexity))
    conn.commit()
    conn.close()

def get_user_passwords(username):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute('SELECT service, password, length, complexity, created_at FROM passwords WHERE username = ? ORDER BY created_at DESC', 
                        (username,)).fetchall()
    conn.close()
    return [{'service': r[0], 'password': r[1], 'length': r[2], 'complexity': r[3], 'timestamp': r[4]} for r in rows]

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    users = [row[0] for row in conn.execute('SELECT username FROM users').fetchall()]
    conn.close()
    return users

def get_all_passwords():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute('SELECT username, service, password, length, complexity, created_at FROM passwords ORDER BY created_at DESC').fetchall()
    conn.close()
    return [{'username': r[0], 'service': r[1], 'password': r[2], 'length': r[3], 'complexity': r[4], 'timestamp': r[5]} for r in rows]
