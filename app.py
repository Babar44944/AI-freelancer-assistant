"""
AI Freelancer Assistant - Day 1
Project Setup, Authentication & Dashboard
Single-file Flask app with auto-install + auto-launch.

Run:  python app.py
"""

import subprocess
import sys
import os

# ---------------- AUTO INSTALL ----------------
REQUIRED = ["flask", "flask_sqlalchemy", "flask_login", "werkzeug"]


def install_requirements():
    import importlib
    for pkg in REQUIRED:
        mod_name = pkg.replace("flask_", "flask_") if pkg.startswith("flask_") else pkg
        try:
            importlib.import_module(mod_name)
        except ImportError:
            print(f"Installing {pkg} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


install_requirements()

from flask import Flask, render_template_string, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

# ---------------- APP CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'freelancer_assistant.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


# ---------------- DATABASE MODELS ----------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bio = db.Column(db.Text, default="")
    skills = db.Column(db.String(500), default="")
    hourly_rate = db.Column(db.Float, default=0.0)
    ai_credits = db.Column(db.Integer, default=50)
    total_proposals = db.Column(db.Integer, default=0)
    total_cover_letters = db.Column(db.Integer, default=0)
    active_clients = db.Column(db.Integer, default=0)
    total_invoices = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- TEMPLATES (Inline) ----------------
BASE_CSS = """
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI', sans-serif; }
body { background: linear-gradient(135deg,#0f172a,#1e293b); min-height:100vh; color:#e2e8f0; }
.navbar { display:flex; justify-content:space-between; align-items:center; padding:18px 40px;
  background:rgba(15,23,42,0.9); border-bottom:1px solid #334155; }
.navbar h2 { color:#38bdf8; }
.navbar a { color:#e2e8f0; text-decoration:none; margin-left:20px; font-size:14px; }
.navbar a:hover { color:#38bdf8; }
.container { max-width:480px; margin:60px auto; background:#1e293b; padding:40px;
  border-radius:14px; box-shadow:0 8px 30px rgba(0,0,0,0.4); }
.container h2 { color:#38bdf8; margin-bottom:20px; text-align:center; }
.form-group { margin-bottom:16px; }
label { display:block; margin-bottom:6px; font-size:14px; color:#94a3b8; }
input { width:100%; padding:11px 14px; border-radius:8px; border:1px solid #334155;
  background:#0f172a; color:#e2e8f0; font-size:14px; }
input:focus { outline:none; border-color:#38bdf8; }
button { width:100%; padding:12px; border:none; border-radius:8px; background:#38bdf8;
  color:#0f172a; font-weight:600; font-size:15px; cursor:pointer; margin-top:8px; }
button:hover { background:#0ea5e9; }
.link-row { text-align:center; margin-top:16px; font-size:13px; }
.link-row a { color:#38bdf8; text-decoration:none; }
.flash { padding:10px 14px; border-radius:8px; margin-bottom:14px; font-size:14px; }
.flash.success { background:#064e3b; color:#6ee7b7; }
.flash.danger { background:#7f1d1d; color:#fca5a5; }
.flash.warning { background:#78350f; color:#fde68a; }
.dash-wrap { max-width:1100px; margin:40px auto; padding:0 20px; }
.dash-header { margin-bottom:30px; }
.dash-header h1 { color:#f1f5f9; }
.dash-header p { color:#94a3b8; margin-top:6px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; margin-bottom:30px; }
.card { background:#1e293b; padding:22px; border-radius:12px; border:1px solid #334155; }
.card .num { font-size:30px; font-weight:700; color:#38bdf8; }
.card .label { font-size:13px; color:#94a3b8; margin-top:6px; }
.section { background:#1e293b; padding:24px; border-radius:12px; border:1px solid #334155; margin-bottom:20px; }
.section h3 { color:#f1f5f9; margin-bottom:16px; }
.activity { padding:10px 0; border-bottom:1px solid #334155; font-size:14px; color:#cbd5e1; }
.quick-actions { display:flex; flex-wrap:wrap; gap:12px; }
.quick-actions button { width:auto; padding:10px 18px; }
</style>
"""

REGISTER_HTML = """
<!doctype html><html><head><title>Register - AI Freelancer Assistant</title>{{ css|safe }}</head>
<body>
<div class="container">
<h2>Create Account</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for cat, msg in messages %}<div class="flash {{cat}}">{{ msg }}</div>{% endfor %}
{% endwith %}
<form method="POST">
  <div class="form-group"><label>Full Name</label><input name="full_name" required></div>
  <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
  <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
  <button type="submit">Register</button>
</form>
<div class="link-row">Already have an account? <a href="{{ url_for('login') }}">Login</a></div>
</div>
</body></html>
"""

LOGIN_HTML = """
<!doctype html><html><head><title>Login - AI Freelancer Assistant</title>{{ css|safe }}</head>
<body>
<div class="container">
<h2>Welcome Back</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for cat, msg in messages %}<div class="flash {{cat}}">{{ msg }}</div>{% endfor %}
{% endwith %}
<form method="POST">
  <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
  <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
  <button type="submit">Login</button>
</form>
<div class="link-row"><a href="{{ url_for('forgot_password') }}">Forgot Password?</a></div>
<div class="link-row">No account? <a href="{{ url_for('register') }}">Register</a></div>
</div>
</body></html>
"""

FORGOT_HTML = """
<!doctype html><html><head><title>Forgot Password</title>{{ css|safe }}</head>
<body>
<div class="container">
<h2>Reset Password</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for cat, msg in messages %}<div class="flash {{cat}}">{{ msg }}</div>{% endfor %}
{% endwith %}
<form method="POST">
  <div class="form-group"><label>Registered Email</label><input type="email" name="email" required></div>
  <button type="submit">Send Reset Link (Demo)</button>
</form>
<div class="link-row"><a href="{{ url_for('login') }}">Back to Login</a></div>
</div>
</body></html>
"""

RESET_HTML = """
<!doctype html><html><head><title>Set New Password</title>{{ css|safe }}</head>
<body>
<div class="container">
<h2>Set New Password</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for cat, msg in messages %}<div class="flash {{cat}}">{{ msg }}</div>{% endfor %}
{% endwith %}
<form method="POST">
  <div class="form-group"><label>New Password</label><input type="password" name="password" required></div>
  <button type="submit">Update Password</button>
</form>
</div>
</body></html>
"""

DASHBOARD_HTML = """
<!doctype html><html><head><title>Dashboard - AI Freelancer Assistant</title>{{ css|safe }}</head>
<body>
<div class="navbar">
  <h2>AI Freelancer Assistant</h2>
  <div>
    <span>{{ current_user.full_name }}</span>
    <a href="{{ url_for('logout') }}">Logout</a>
  </div>
</div>
<div class="dash-wrap">
  <div class="dash-header">
    <h1>Welcome back, {{ current_user.full_name.split(' ')[0] }} 👋</h1>
    <p>Here's what's happening with your freelance business today.</p>
  </div>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for cat, msg in messages %}<div class="flash {{cat}}">{{ msg }}</div>{% endfor %}
  {% endwith %}

  <div class="grid">
    <div class="card"><div class="num">{{ profile.total_proposals }}</div><div class="label">Total Generated Proposals</div></div>
    <div class="card"><div class="num">{{ profile.total_cover_letters }}</div><div class="label">Cover Letters Created</div></div>
    <div class="card"><div class="num">{{ profile.active_clients }}</div><div class="label">Active Clients</div></div>
    <div class="card"><div class="num">{{ profile.total_invoices }}</div><div class="label">Total Invoices</div></div>
    <div class="card"><div class="num">{{ profile.ai_credits }}</div><div class="label">AI Credits Remaining</div></div>
  </div>

  <div class="section">
    <h3>Quick Actions</h3>
    <div class="quick-actions">
      <button disabled title="Coming Day 2">Generate Proposal</button>
      <button disabled title="Coming Day 2">Write Cover Letter</button>
      <button disabled title="Coming Day 3">Create Invoice</button>
      <button disabled title="Coming Day 3">Draft Contract</button>
    </div>
  </div>

  <div class="section">
    <h3>Recent Activity</h3>
    <div class="activity">✅ Account created successfully</div>
    <div class="activity">🔐 Logged in to dashboard</div>
    <div class="activity">⚙️ AI modules will be wired in Day 2-3</div>
  </div>
</div>
</body></html>
"""


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        user = User(full_name=full_name, email=email, is_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template_string(REGISTER_HTML, css=BASE_CSS)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template_string(LOGIN_HTML, css=BASE_CSS)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(16)
            user.reset_token = token
            db.session.commit()
            # Demo mode: show reset link directly instead of sending email
            flash(f"Demo reset link: /reset-password/{token}", "success")
        else:
            flash("If that email exists, a reset link has been generated.", "warning")
        return redirect(url_for("forgot_password"))

    return render_template_string(FORGOT_HTML, css=BASE_CSS)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password", "")
        if not new_password:
            flash("Password cannot be empty.", "danger")
            return redirect(url_for("reset_password", token=token))
        user.set_password(new_password)
        user.reset_token = None
        db.session.commit()
        flash("Password updated successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template_string(RESET_HTML, css=BASE_CSS)


@app.route("/dashboard")
@login_required
def dashboard():
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    return render_template_string(DASHBOARD_HTML, css=BASE_CSS, profile=profile)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------------- DB INIT + AUTO RUN ----------------
def init_db():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("AI Freelancer Assistant - Day 1 (Auth + Dashboard)")
    print("Running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
