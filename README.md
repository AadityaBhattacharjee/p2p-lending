# 💸 DeFi Loan Platform

A Peer-to-Peer Emergency Loan Platform for underserved communities. This system provides microloans without traditional credit scores, using social trust metrics, a blockchain ledger, and lender funding.

---

## 🚀 Features

- ✅ User registration with OTP verification (Twilio SMS)
- ✅ Loan approval based on trust score (trained ML model)
- ✅ Repayment tracking with on-chain ledger
- ✅ Blockchain simulation with hashed transactions
- ✅ Lender registration and dashboard
- ✅ SQLite-powered backend with Flask

---

## 🧰 Tech Stack & Packages

### 🔙 Backend
- **Flask** – Web framework
- **Gunicorn** – Production WSGI server (Render deployment)
- **SQLite3** – Lightweight local database
- **scikit-learn** – ML model for trust scoring
- **pandas / numpy** – Data preprocessing
- **joblib** – Model serialization
- **Twilio** – SMS OTP delivery
- **dotenv** – Secure credential management

### 🎨 Frontend
- HTML + CSS (Dark lime-glow UI theme)
- JavaScript (status/animations)
- Jinja2 templating (Flask integration)


---

## 🌐 Deployment (Render)

### Required Files
- `app.py`
- `blockchain.py`
- `otp.py`
- `trust_model.py`
- `db.py`
- `requirements.txt`
- `Procfile`

### Render Configuration

- **Start Command:** `gunicorn app:app`
- **Environment Variables:**

## 🔐 Twilio Free Tier Limitations

- You can **only send SMS to verified phone numbers**
- All outbound SMS have a **"Sent from your Twilio trial account"** prefix
- **OTP delivery delays** can occur due to trial restrictions
- You'll need to **upgrade** and **register a proper sender ID (A2P 10DLC)** to send to public numbers (India, US, etc.)

> 📌 Workaround: For demos, verify your own phone via [Twilio Console → Verified Caller IDs](https://console.twilio.com)

