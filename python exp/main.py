import streamlit as st
import sqlite3
from datetime import datetime

conn = sqlite3.connect('banking_system.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, balance REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions 
             (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, 
              transaction_type TEXT, date TEXT, FOREIGN KEY(user_id) REFERENCES users(user_id))''')

def create_user(username, password):
    c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (username, password, 0.0))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def update_balance(user_id, amount, transaction_type):
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id) if transaction_type == 'deposit' else (-amount, user_id))
    conn.commit()
    record_transaction(user_id, amount, transaction_type)

def record_transaction(user_id, amount, transaction_type):
    c.execute("INSERT INTO transactions (user_id, amount, transaction_type, date) VALUES (?, ?, ?, ?)", (user_id, amount, transaction_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def view_balance(user_id):
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    return c.fetchone()[0]

def view_transactions(user_id):
    c.execute("SELECT amount, transaction_type, date FROM transactions WHERE user_id=?", (user_id,))
    return c.fetchall()

def main():
    st.title("Banking System")
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sign Up":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            create_user(new_user, new_password)
            st.success("Account created successfully!")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome, {username}!")
                balance = view_balance(user[0])
                st.write(f"Your current balance is ₹{balance}")

                options = ["Deposit", "Withdraw", "View Transactions"]
                action = st.selectbox("Action", options)

                if action == "Deposit":
                    amount = st.number_input("Enter amount to deposit", min_value=1.0)
                    if st.button("Deposit"):
                        update_balance(user[0], amount, 'deposit')
                        st.success(f"₹{amount} deposited successfully!")

                elif action == "Withdraw":
                    amount = st.number_input("Enter amount to withdraw", min_value=1.0, max_value=balance)
                    if st.button("Withdraw"):
                        update_balance(user[0], amount, 'withdraw')
                        st.success(f"₹{amount} withdrawn successfully!")

                elif action == "View Transactions":
                    st.subheader("Transaction History")
                    transactions = view_transactions(user[0])
                    for t in transactions:
                        st.write(f"₹{t[0]} | {t[1]} | {t[2]}")

            else:
                st.error("Invalid username or password")

if __name__ == '__main__':
    main()
