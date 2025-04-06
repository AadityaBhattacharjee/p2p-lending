import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create transactions table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ✅ Create lenders table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS lenders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            funds REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def insert_transaction(phone, amount, status):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (phone, amount, status) VALUES (?, ?, ?)", (phone, amount, status))
    conn.commit()
    conn.close()
