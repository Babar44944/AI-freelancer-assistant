# 🤖 AI Freelancer Assistant

> A complete AI-powered web application that helps freelancers automate their daily workflow — proposals, cover letters, invoices, contracts, and more.

---

## 📋 Project Overview

This project is built as a **5-Day Internship Project**. It uses AI APIs to generate freelancing documents and provides a full-featured dashboard to manage freelance work efficiently.

**Duration:** 5 Days  
**Stack:** Python · Flask · SQLite · Flask-Login · Werkzeug

## ✅ Day 1 — Features Implemented

### 🔐 Authentication System
- User Registration (Full Name, Email, Password)
- User Login with session management
- Logout
- Forgot Password (with demo reset link)
- Password Reset via secure token
- Secure password hashing (Werkzeug)

### 📊 Dashboard Widgets
- Total Generated Proposals
- Cover Letters Created
- Active Clients
- Total Invoices
- AI Credits Remaining
- Recent Activity Feed
- Quick Actions (unlocked in Day 2+)

### 🗄️ Database Tables
- `users` — stores user credentials and account info
- `user_profiles` — stores freelancer stats and AI credit balance

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or above
- pip

### Run the App

```bash
# Clone the repo
git clone https://github.com/Babar44944/ai-freelancer-assistant.git

# Navigate to project folder
cd ai-freelancer-assistant

# Run the app (auto-installs dependencies)
python app.py
```

> App will open at: **http://127.0.0.1:5000**

All dependencies are **auto-installed** on first run. No need to manually run `pip install`.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| Flask-SQLAlchemy | Database ORM |
| Flask-Login | Session & auth management |
| Werkzeug | Password hashing |

---

## 📁 Project Structure

```
ai-freelancer-assistant/
│
├── app.py                    # Main application (single-file, Day 1)
├── freelancer_assistant.db   # SQLite database (auto-created)
└── README.md                 # Project documentation
```


## 👨‍💻 Author

**Babar Ali**  
AI/ML Developer | Python · Flask · Machine Learning  
📍 Pakistan  

his project is built for internship/educational purposes.
