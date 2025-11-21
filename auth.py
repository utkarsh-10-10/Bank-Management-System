import sqlite3
import random
from database import get_connection

def create_account(name, pin):
    conn = get_connection()
    cursor = conn.cursor()
    
    while True:
        acc_num = random.randint(100000, 999999)
        try:
            cursor.execute("INSERT INTO users (account_number, name, pin, balance) VALUES (?, ?, ?, 0.0)", 
                           (acc_num, name, pin))
            conn.commit()
            conn.close()
            return acc_num
        except sqlite3.IntegrityError:
            continue

def login(account_number, pin):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE account_number = ? AND pin = ?", (account_number, pin))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "account_number": user[0],
            "name": user[1],
            "pin": user[2],
            "balance": user[3]
        }
    return None

def admin_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
    admin = cursor.fetchone()
    conn.close()
    
    return admin is not None