import csv
import sqlite3
from datetime import datetime, timedelta, timezone
from database import get_connection
from tabulate import tabulate

# HELPER FUNCTIONS

def get_user_name(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE account_number = ?", (account_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_ist_time():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    return now_ist.strftime("%Y-%m-%d %H:%M:%S")

# USER OPERATIONS

def get_balance(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def deposit(account_number, amount):
    if amount <= 0: return False, "Amount must be positive."
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT name FROM users WHERE account_number = ?", (account_number,))
        name = cursor.fetchone()[0]

        cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, account_number))
        cursor.execute("INSERT INTO transactions (account_number, name, transaction_type, amount, timestamp) VALUES (?, ?, 'DEPOSIT', ?, ?)", 
                       (account_number, name, amount, current_time))
        
        cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        return True, f"Deposit successful. New Balance: ₹ {new_balance:.2f}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def withdraw(account_number, amount):
    balance = get_balance(account_number)
    if amount <= 0: return False, "Amount must be positive."
    if balance < amount: return False, "Insufficient funds."
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT name FROM users WHERE account_number = ?", (account_number,))
        name = cursor.fetchone()[0]

        cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, account_number))
        cursor.execute("INSERT INTO transactions (account_number, name, transaction_type, amount, timestamp) VALUES (?, ?, 'WITHDRAWAL', ?, ?)", 
                       (account_number, name, amount, current_time))
        
        cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
        new_balance = cursor.fetchone()[0]
        
        conn.commit()
        return True, f"Withdrawal successful. Remaining Balance: ₹ {new_balance:.2f}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def transfer_funds(sender_acc, receiver_acc, amount):
    sender_bal = get_balance(sender_acc)
    if amount <= 0: return False, "Amount must be positive."
    if sender_bal < amount: return False, "Insufficient funds."
    if str(sender_acc) == str(receiver_acc): return False, "Cannot transfer to self."
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT account_number, name FROM users WHERE account_number = ?", (receiver_acc,))
        receiver_data = cursor.fetchone()
        if not receiver_data: return False, "Receiver account not found."
        receiver_name = receiver_data[1]

        cursor.execute("SELECT name FROM users WHERE account_number = ?", (sender_acc,))
        sender_name = cursor.fetchone()[0]

        cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, sender_acc))
        cursor.execute("INSERT INTO transactions (account_number, name, transaction_type, amount, timestamp) VALUES (?, ?, 'TRANSFER_SENT', ?, ?)", 
                       (sender_acc, sender_name, amount, current_time))
        
        cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, receiver_acc))
        cursor.execute("INSERT INTO transactions (account_number, name, transaction_type, amount, timestamp) VALUES (?, ?, 'TRANSFER_RECEIVED', ?, ?)", 
                       (receiver_acc, receiver_name, amount, current_time))
        
        conn.commit()
        return True, "Transfer successful."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def print_history(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_type, amount, timestamp FROM transactions WHERE account_number = ? ORDER BY id DESC LIMIT 10", (account_number,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["Type", "Amount", "Time (IST)"], tablefmt="fancy_grid"))
    else:
        print("No transactions found.")

def check_loan_eligibility(account_number):
    balance = get_balance(account_number)
    if balance >= 5000:
        return True, balance * 5
    return False, 0.0

def update_pin(account_number, new_pin):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET pin = ? WHERE account_number = ?", (new_pin, account_number))
        conn.commit()
        return True, "PIN updated successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def close_account(account_number):
    balance = get_balance(account_number)
    if balance > 0:
        return False, "Cannot close account with remaining balance. Please withdraw funds first."
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT * FROM users WHERE account_number = ?", (account_number,))
        user_data = cursor.fetchone()
        
        if user_data:
            cursor.execute("INSERT INTO deleted_users (account_number, name, pin, balance, closed_at) VALUES (?, ?, ?, ?, ?)", 
                           (user_data[0], user_data[1], user_data[2], user_data[3], current_time))

        cursor.execute("DELETE FROM users WHERE account_number = ?", (account_number,))
        conn.commit()
        return True, "Account closed successfully. Records archived."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def submit_complaint(account_number, message):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT name FROM users WHERE account_number = ?", (account_number,))
        name = cursor.fetchone()[0]

        cursor.execute("INSERT INTO complaints (account_number, name, message, timestamp) VALUES (?, ?, ?, ?)", 
                       (account_number, name, message, current_time))
        conn.commit()
        return True, "Feedback submitted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ADMIN OPERATIONS

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_number, name, balance FROM users")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["Acc Num", "Name", "Balance"], tablefmt="fancy_grid"))
    else:
        print("No active users.")

def get_deleted_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_number, name, closed_at FROM deleted_users")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["Acc Num", "Name", "Closed At (IST)"], tablefmt="fancy_grid"))
    else:
        print("No deleted user records found.")

def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, account_number, name, transaction_type, amount, timestamp FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["ID", "Acc Num", "Name", "Type", "Amount", "Time (IST)"], tablefmt="fancy_grid"))
    else:
        print("No transactions recorded yet.")

def get_all_complaints():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, account_number, name, message, timestamp FROM complaints ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["ID", "Acc Num", "Name", "Message", "Time (IST)"], tablefmt="fancy_grid"))
    else:
        print("No complaints found.")

def add_new_admin(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, f"New Admin '{username}' added."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def apply_interest_to_all():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        current_time = get_ist_time()
        
        cursor.execute("SELECT account_number, name, balance FROM users")
        users = cursor.fetchall()
        
        count = 0
        for acc_num, name, balance in users:
            if balance > 0:
                interest = balance * 0.05
                new_balance = balance + interest
                cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", (new_balance, acc_num))
                cursor.execute("INSERT INTO transactions (account_number, name, transaction_type, amount, timestamp) VALUES (?, ?, 'INTEREST_CREDIT', ?, ?)", 
                               (acc_num, name, interest, current_time))
                count += 1
        conn.commit()
        return True, f"Interest applied to {count} accounts."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def export_transactions_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    filename = "bank_transactions_report.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Account Number", "Name", "Type", "Amount", "Timestamp (IST)"])
            writer.writerows(rows)
        return True, f"Report saved as '{filename}'"
    except Exception as e:
        return False, str(e)