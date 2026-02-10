from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "neoinbox-super-secret"

DB_PATH = "neoinbox.db"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

# ---------- BASE TEMPLATE ----------
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>{{ title }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
:root{
--bg:#0f2027;--card:rgba(255,255,255,.08);--text:white;
}
.light{
--bg:#f4f6f8;--card:white;--text:#222;
}
*{box-sizing:border-box;font-family:Inter}
body{
margin:0;background:var(--bg);color:var(--text);
transition:0.3s;
}
header{
padding:20px 40px;
display:flex;justify-content:space-between;align-items:center;
}
a{color:inherit;text-decoration:none;margin-left:20px}
.toggle{
cursor:pointer;padding:8px 14px;border-radius:20px;
background:rgba(255,255,255,.15);
}
.hero{text-align:center;padding:100px 20px}
.card{
background:var(--card);
max-width:400px;margin:80px auto;
padding:30px;border-radius:20px;
animation:up .7s ease;
}
@keyframes up{from{opacity:0;transform:translateY(40px)}}
input,button{
width:100%;padding:14px;margin-top:12px;
border:none;border-radius:12px;
}
button{
background:linear-gradient(90deg,#00e5ff,#00bcd4);
font-weight:600;cursor:pointer;
}
</style>
</head>

<body>
<header>
<h2>NeoInbox</h2>
<div>
<span class="toggle" onclick="toggleMode()">🌙 / ☀️</span>
{% if session.get("user") %}
<a href="/logout">Logout</a>
{% else %}
<a href="/login">Login</a>
<a href="/signup">Sign Up</a>
{% endif %}
</div>
</header>

{{ body|safe }}

<script>
function toggleMode(){
document.body.classList.toggle("light");
localStorage.setItem("mode",document.body.classList.contains("light"));
}
if(localStorage.getItem("mode")==="true"){
document.body.classList.add("light");
}
</script>
</body>
</html>
"""

# ---------- ROUTES ----------
@app.route("/")
def home():
    if session.get("user"):
        body = f"""
        <div class="hero">
        <h1>Welcome, {session['user']}</h1>
        <p>Your secure smart inbox</p>
        </div>
        """
    else:
        body = """
        <div class="hero">
        <h1>The Future of Smart Messaging</h1>
        <p>Secure • Fast • Minimal</p>
        </div>
        """
    return render_template_string(BASE_HTML, title="NeoInbox", body=body)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                    (name,email,password)
                )
            return redirect("/login")
        except:
            pass

    body = """
    <form class="card" method="post">
    <h2>Sign Up</h2>
    <input name="name" placeholder="Name" required>
    <input name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button>Create Account</button>
    </form>
    """
    return render_template_string(BASE_HTML, title="Sign Up", body=body)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",(email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["name"]
            return redirect("/")

    body = """
    <form class="card" method="post">
    <h2>Login</h2>
    <input name="email" placeholder="Email" required>
    <input type="password" name="password" placeholder="Password" required>
    <button>Login</button>
    </form>
    """
    return render_template_string(BASE_HTML, title="Login", body=body)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RENDER ENTRY ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

