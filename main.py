import sys
import time
import pyfiglet
from tabulate import tabulate
import database
import auth
import operations

Menu = [
    [1, 'User Login'],
    [2, 'Create New Account'],
    [3, 'Admin Login'],
    [4, 'Exit']
]

def main():
    database.init_db()
    show_banner()
    
    while True:
        try:
            print(tabulate(Menu, headers=['OPTION', 'FUNCTION'], tablefmt="fancy_grid", stralign="center", numalign="center"))
            ch = input("\nChoose Option Number From Menu: ").strip()
            
            if ch == '1':
                user_login_flow()
            elif ch == '2':
                create_account_flow()
            elif ch == '3':
                admin_login_flow()
            elif ch == '4':
                print("\nQuitting The Program...")
                break
            else:
                print("\nInvalid Choice, Select(1-4).\n")
                
        except KeyboardInterrupt:
            sys.exit('\n')

def show_banner():
    print()
    print("============================================================")
    try:
        print(pyfiglet.figlet_format("Bank Management", font="doom"))
        print(pyfiglet.figlet_format("System", font="doom"))
    except Exception:
        print("       BANK MANAGEMENT SYSTEM       ")
    print("============================================================")
    print(" A command-line tool to manage bank accounts, transactions,")
    print(" loans, interest, and more — all in a secure environment.")
    print("============================================================")
    print()

def user_login_flow():
    print("\n--- USER LOGIN ---")
    try:
        acc_input = input("Account Num: ").strip()
        if not acc_input: return 
        acc = int(acc_input)
        
        pin_input = input("PIN: ").strip()
        if not pin_input: return 
        pin = int(pin_input)
        
        user = auth.login(acc, pin)
        if user:
            user_dashboard(user)
        else:
            print("\n[ERROR] Invalid Credentials. Access Denied.\n")
    except ValueError:
        print("\n[ERROR] Input must be numbers only.\n")

def create_account_flow():
    print("\n--- CREATE NEW ACCOUNT ---")
    while True:
        name = input("Enter Full Name (or press Enter to Cancel): ").strip()
        if not name:
            print("Registration Cancelled.\n")
            return
        
        try:
            pin_input = input("Set a 4-digit PIN: ").strip()
            if not pin_input.isdigit():
                print("[ERROR] PIN must contain numbers only.")
                continue
                
            pin = int(pin_input)
            if len(pin_input) == 4:
                acc = auth.create_account(name, pin)
                print(f"\n[SUCCESS] Account Created!")
                print(f"IMPORTANT: Your Account Number is {acc}")
                print("Please write this down to login.\n")
                input("Press Enter to return to Main Menu...")
                break
            else: 
                print("[ERROR] PIN must be exactly 4 digits.")
        except ValueError: 
            print("[ERROR] Invalid input.")

def admin_login_flow():
    print("\n--- ADMIN LOGIN ---")
    user = input("Admin Username: ").strip()
    password = input("Admin Password: ").strip()
    
    if auth.admin_login(user, password):
        print("\nAdmin Verified.")
        time.sleep(0.5)
        admin_dashboard()
    else: 
        print("\n[ERROR] Invalid Admin Credentials.\n")

def user_dashboard(user):
    while True:
        print(f"\n--- DASHBOARD: {user['name']} ---")
        user_menu = [
            ["1", "Check Balance"], 
            ["2", "Deposit"], 
            ["3", "Withdraw"], 
            ["4", "Transfer"], 
            ["5", "My History"], 
            ["6", "Loan Eligibility"],
            ["7", "Change PIN"],
            ["8", "Close Account"],
            ["9", "Feedback"], 
            ["10", "Logout"]
        ]
        print(tabulate(user_menu, tablefmt="fancy_grid", stralign="left"))
        
        try:
            choice = input("\nSelect Action: ").strip()
            
            if choice == '1':
                print(f"\nBalance: ₹ {operations.get_balance(user['account_number']):.2f}")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '2':
                try:
                    amt_str = input("Enter amount to Deposit: ")
                    if amt_str:
                        amt = float(amt_str)
                        success, msg = operations.deposit(user['account_number'], amt)
                        print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                except ValueError: print("Invalid input.")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '3':
                try:
                    amt_str = input("Enter amount to Withdraw: ")
                    if amt_str:
                        amt = float(amt_str)
                        success, msg = operations.withdraw(user['account_number'], amt)
                        print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                except ValueError: print("Invalid input.")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '4':
                target_input = input("Receiver Account Number (Enter to cancel): ")
                if target_input:
                    try:
                        target_acc = int(target_input)
                        receiver_name = operations.get_user_name(target_acc)
                        if receiver_name:
                            print(f"\n[VERIFY] Transferring to: {receiver_name}")
                            if input("Confirm? (y/n): ").lower() in ['y', 'yes']:
                                amt = float(input("Amount: "))
                                success, msg = operations.transfer_funds(user['account_number'], target_acc, amt)
                                print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                            else: print("Cancelled.")
                        else: print("\n[ERROR] Account Not Found.")
                    except ValueError: print("Invalid input.")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '5':
                operations.print_history(user['account_number'])
                input("\nPress Enter to return to Dashboard...")

            elif choice == '6':
                eligible, amount = operations.check_loan_eligibility(user['account_number'])
                if eligible:
                    print(f"\n[CONGRATS] Eligible for loan up to ₹ {amount:.2f}")
                else:
                    print(f"\n[SORRY] Minimum balance of ₹ 5000 required.")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '7':
                try:
                    new_pin = int(input("Enter New 4-digit PIN: "))
                    if len(str(new_pin)) == 4:
                        success, msg = operations.update_pin(user['account_number'], new_pin)
                        print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                    else: print("PIN must be 4 digits.")
                except ValueError: print("Invalid input.")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '8':
                confirm = input("Close Account permanently? (yes/no): ").lower()
                if confirm in ['y', 'yes']:
                    success, msg = operations.close_account(user['account_number'])
                    print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                    if success: return
                input("\nPress Enter to return to Dashboard...")

            elif choice == '9':
                msg = input("Message: ")
                if msg:
                    success, resp = operations.submit_complaint(user['account_number'], msg)
                    print(f"\n[{'SUCCESS' if success else 'ERROR'}] {resp}")
                input("\nPress Enter to return to Dashboard...")

            elif choice == '10':
                break
            
            else:
                print("\nInvalid Choice.")
                
        except KeyboardInterrupt:
            print("\nLogging out...")
            break

def admin_dashboard():
    while True:
        print("\n--- ADMIN DASHBOARD ---")
        admin_menu = [
            ["1", "View Users"],
            ["2", "View Transactions"],
            ["3", "Apply Interest (5%)"],
            ["4", "Download CSV"],
            ["5", "View Complaints"],
            ["6", "View Deleted Users"], 
            ["7", "Add New Admin"],
            ["8", "Logout"]
        ]
        print(tabulate(admin_menu, tablefmt="fancy_grid", stralign="left"))
        
        try:
            choice = input("\nSelect Action: ").strip()
            
            if choice == '1':
                operations.get_all_users()
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '2':
                operations.get_all_transactions()
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '3':
                confirm = input("Apply 5% interest to ALL users? (yes/no): ").lower()
                if confirm in ['y', 'yes']:
                    success, msg = operations.apply_interest_to_all()
                    print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                else:
                    print("\nOperation Cancelled.")
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '4':
                success, msg = operations.export_transactions_csv()
                print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '5':
                operations.get_all_complaints()
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '6':
                print("\n--- DELETED / PAST USERS RECORDS ---")
                operations.get_deleted_users()
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '7':
                print("\n--- ADD NEW ADMIN ---")
                new_user = input("Enter New Admin Username: ").strip()
                if new_user:
                    new_pass = input("Enter New Admin Password: ").strip()
                    if new_pass:
                        success, msg = operations.add_new_admin(new_user, new_pass)
                        print(f"\n[{'SUCCESS' if success else 'ERROR'}] {msg}")
                    else:
                        print("\n[ERROR] Password cannot be empty.")
                else:
                    print("\n[ERROR] Username cannot be empty.")
                input("\nPress Enter to return to Admin Menu...")

            elif choice == '8':
                break
            
            else:
                print("\nInvalid Choice.")

        except KeyboardInterrupt:
            print("\nLogging out...")
            break

if __name__ == "__main__":
    main()