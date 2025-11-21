import sqlite3
import os

DB_NAME = "bank.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            account_number INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            pin INTEGER NOT NULL,
            balance REAL DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deleted_users (
            account_number INTEGER PRIMARY KEY,
            name TEXT,
            pin INTEGER,
            balance REAL,
            closed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER,
            name TEXT,
            transaction_type TEXT,
            amount REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER,
            name TEXT,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    
    conn.commit()
    conn.close()
    
    if not os.path.exists(DB_NAME):
        print(f"[System] Database {DB_NAME} created.")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")