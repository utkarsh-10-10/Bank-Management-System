# Bank Management System

A robust Command Line Interface (CLI) application developed in Python to simulate core banking operations. This system is designed to demonstrate **Computational Thinking** by implementing logic for account management, financial transactions, and administrative oversight using a local database.

## 📌 Project Overview

This project simulates a banking environment where users can perform daily financial tasks and administrators can monitor the bank's health. It prioritizes data integrity (using ACID properties of SQLite) and user experience (using structured tables and clear prompts).

**Key Feature:** All transaction timestamps are automatically calculated and stored in **Indian Standard Time (IST)**, ensuring accurate local logging regardless of the system's default UTC time.

## ✨ Features

### 👤 User Services
* **Account Creation:** Auto-generates a unique 6-digit Account Number upon registration.
* **Financial Operations:**
    * **Deposit & Withdraw:** Real-time balance updates.
    * **Fund Transfer:** Secure transfer system that **verifies the Receiver's Name** before sending money to prevent errors.
* **Transaction History:** View the last 10 transactions with precise IST timestamps.
* **Loan Eligibility:** Automated logic to check if a user qualifies for a loan (Requires minimum balance > ₹5000).
* **Account Management:**
    * **Change PIN:** Users can update their security PIN.
    * **Close Account:** "Soft delete" functionality that archives the user data to a separate history table (`deleted_users`) instead of deleting it permanently, preserving audit trails.
* **Feedback:** Submit complaints or feedback directly to the bank admin.

### 🛡️ Admin Dashboard
* **User Management:** View all active users and their balances.
* **Audit Archives:** View records of **Deleted/Closed Accounts** (Past Users).
* **Global Transaction Log:** A master view of every deposit, withdrawal, and transfer in the bank.
* **Interest Calculation:** One-click feature to apply **5% Interest** to all active user accounts simultaneously.
* **Data Export:** Generates a `bank_transactions_report.csv` file for external analysis in Excel.
* **Admin Management:** Existing admins can add new administrators to the system.
* **Feedback Review:** Read complaints submitted by customers.

## 🛠️ Tech Stack & Limitations

* **Language:** Python 3.x
* **Database:** SQLite3 (Local storage).
* **Libraries:** `tabulate` (Tables), `pyfiglet` (ASCII Art), `csv`, `datetime`.

### ⚠️ Educational Note (Security)
This project is an **educational prototype**. To demonstrate the underlying logic clearly:
* **Passwords & PINs:** Stored as **plain text/integers** in the database. No hashing (SHA/BCrypt) is currently implemented to allow for easier debugging and logic demonstration during the evaluation.
* **Storage:** The database (`bank.db`) is a local file and not encrypted.

## 📂 Project Structure

```text
Bank-Management-System/
│
├── main.py           # Entry point. Handles Menus, UI logic, and flow control.
├── auth.py           # Handles Login and Account Creation logic.
├── operations.py     # Core functions (Deposit, Withdraw, IST Time, SQL queries).
├── database.py       # Handles Schema creation, Table setup, and Admin initialization.
├── requirements.txt  # List of external libraries.
└── README.md         # Project documentation.
```
## 🚀 How to Run

### Install Dependencies
Open your terminal/command prompt in the project folder and run:

```pip install -r requirements.txt```

### Run the Application:

```python main.py```
(The database file bank.db will be created automatically on the first run).

## 🔑 Default Admin Credentials
Use these credentials to access the Admin Dashboard for the first time:

```Username: admin```
```Password: admin123```

## 📝 Team Name
**Code Wizards**

Computational Thinking and Programming Project (2025CSET100)
