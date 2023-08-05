
import sqlite3


def create_admin_user():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    # Verificamos si la tabla existe, y si no, la creamos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Verificamos si el usuario administrador ya existe, y si no, lo creamos
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))

    connection.commit()
    connection.close()


def login_user(username, password):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    connection.close()

    if user:
        return True
    else:
        return False
