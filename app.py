from flask import Flask, render_template, request, redirect, session
import sqlite3
from otp import send_otp_sms, otp_store, verify_otp
from trust_model import train_model, predict_trust_score
from blockchain import Blockchain
from db import init_db, insert_transaction
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

blockchain = Blockchain()
init_db()
train_model()

@app.route('/')
def index():
    if 'phone' not in session:
        return redirect('/login')

    phone = session['phone']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Fetch loan transactions
    cur.execute("SELECT * FROM transactions WHERE phone=?", (phone,))
    transactions = cur.fetchall()

    # Fetch repayment history (create table if it doesn't exist)
    cur.execute('''CREATE TABLE IF NOT EXISTS repayments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    cur.execute("SELECT * FROM repayments WHERE phone=?", (phone,))
    repayments = cur.fetchall()

    conn.close()

    return render_template('index.html',
                           phone=phone,
                           blockchain=blockchain.to_list(),
                           transactions=transactions,
                           repayments=repayments)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE phone=?", (phone,))
        if cur.fetchone():
            conn.close()
            return 'User already exists'

        send_otp_sms(phone)
        session['temp_user'] = {'name': name, 'phone': phone, 'password': password}
        return redirect('/verify_otp_register')
    return render_template('register.html')

@app.route('/verify_otp_register', methods=['GET', 'POST'])
def verify_otp_register():
    if request.method == 'POST':
        otp = request.form['otp']
        temp_user = session.get('temp_user')
        if not temp_user:
            return redirect('/register')

        if verify_otp(temp_user['phone'], otp):
            conn = sqlite3.connect('users.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name, phone, password) VALUES (?, ?, ?)",
                        (temp_user['name'], temp_user['phone'], temp_user['password']))
            conn.commit()
            conn.close()
            session.pop('temp_user', None)
            return redirect('/login')
        else:
            return 'Invalid or expired OTP'
    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE phone=? AND password=?", (phone, password))
        user = cur.fetchone()
        conn.close()
        if user:
            send_otp_sms(phone)
            session['temp_login'] = phone
            return redirect('/verify_otp_login')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/verify_otp_login', methods=['GET', 'POST'])
def verify_otp_login():
    if request.method == 'POST':
        otp = request.form['otp']
        phone = session.get('temp_login')
        if verify_otp(phone, otp):
            session['phone'] = phone
            session.pop('temp_login', None)
            return redirect('/')
        else:
            return 'Invalid or expired OTP'
    return render_template('verify_otp.html')

@app.route('/apply_loan', methods=['POST'])
def apply_loan():
    if 'phone' not in session:
        return redirect('/login')

    phone = session['phone']
    amount = float(request.form['amount'])
    wallet_txns = int(request.form['wallet_activity'])
    bill_timeliness = int(request.form['bill_timeliness'])
    social_score = float(request.form['social_score'])

    trust_score = predict_trust_score(wallet_txns, bill_timeliness, social_score)
    approved = trust_score >= 0.4
    status = 'Approved' if approved else 'Rejected'

    blockchain.add_block({
        "transaction_data": {
            "amount": amount,
            "status": status
        },
        "user_id": phone
    })

    insert_transaction(phone, amount, status)

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE phone=?", (phone,))
    transactions = cur.fetchall()
    conn.close()

    return render_template('index.html',
                           phone=phone,
                           status=status,
                           blockchain=blockchain.to_list(),
                           transactions=transactions)

@app.route('/repay_loan', methods=['POST'])
def repay_loan():
    if 'phone' not in session:
        return redirect('/login')

    phone = session['phone']
    repay_amount = float(request.form['repay_amount'])

    # Save repayment to DB
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS repayments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    cur.execute("INSERT INTO repayments (phone, amount) VALUES (?, ?)", (phone, repay_amount))
    conn.commit()
    conn.close()

    # Add to blockchain
    blockchain.add_block({
        "transaction_data": {
            "type": "Repayment",
            "amount": repay_amount
        },
        "user_id": phone
    })

    return redirect('/')


@app.route('/add_lender', methods=['GET', 'POST'])
def add_lender():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        funds = float(request.form['funds'])

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO lenders (name, phone, funds) VALUES (?, ?, ?)", (name, phone, funds))
        conn.commit()
        conn.close()

        blockchain.add_block({
            "transaction_data": {
                "type": "Lender Registration",
                "name": name,
                "funds": funds
            },
            "user_id": phone
        })

        return render_template('lender.html', success=True)

    return render_template('lender.html')

@app.route('/lender_dashboard')
def lender_dashboard():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM lenders")
    lenders = cur.fetchall()
    cur.execute("SELECT COUNT(*), SUM(funds) FROM lenders")
    lender_count, total_funds = cur.fetchone()
    conn.close()

    return render_template('lender_dashboard.html', lenders=lenders, lender_count=lender_count, total_funds=total_funds or 0)




@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    import os
    PORT = int(os.environ.get("PORT", 5000))
    print(f"🟢 Starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)

