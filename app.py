from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- LOAD MODEL ----------------
model = joblib.load("model/stock_model.pkl")

# ---------------- USERS DATABASE ----------------
def get_user_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_user_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()
conn.close()

# ---------------- CONTACT DATABASE ----------------
def get_contact_connection():
    conn = sqlite3.connect("contact.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_contact_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL
)
""")
conn.commit()
conn.close()

# ---------------- PREDICTION DATABASE ----------------
def get_prediction_connection():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_prediction_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock TEXT NOT NULL,
    days INTEGER NOT NULL,
    predicted_price REAL NOT NULL
)
""")
conn.commit()
conn.close()

# ---------------- PAGE ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict-page")
def predict_page():
    return render_template("predict.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/work")
def work():
    return render_template("work.html")

@app.route("/dataset")
def dataset():
    return render_template("dataset.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET"])
def login_page():
    print("LOGIN PAGE ROUTE HIT")
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

# ---------------- CONTACT PROCESS ----------------
@app.route("/contact-process", methods=["POST"])
def contact_process():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    conn = get_contact_connection()
    conn.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    conn.commit()
    conn.close()

    flash("Message sent successfully!")
    return redirect(url_for("contact"))

# ---------------- REGISTER PROCESS ----------------
@app.route("/register-process", methods=["POST"])
def register_process():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_user_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        conn.close()

        print("Redirecting to login page")  # DEBUG
        flash("Registration successful! Please login.")
        return redirect(url_for("login_page"))

    except sqlite3.IntegrityError:
        conn.close()
        flash("Username already exists!")
        return redirect(url_for("register_page"))

# ---------------- LOGIN PROCESS ----------------
@app.route("/login-process", methods=["POST"])
def login_process():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_user_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()

    if user:
        flash("Login successful!")
        return redirect(url_for("home"))
    else:
        flash("Invalid username or password!")
        return redirect(url_for("login_page"))


# ---------------- PREDICT (ONLY ONE – FINAL) ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return redirect(url_for("predict_page"))

    stock = request.form["stock"]
    days = int(request.form["days"])

    predicted_price = round(model.predict(np.array([[days]]))[0], 2)

    # Store prediction
    conn = get_prediction_connection()
    conn.execute(
        "INSERT INTO predictions (stock, days, predicted_price) VALUES (?, ?, ?)",
        (stock, days, predicted_price)
    )
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        stock=stock,
        days=days,
        price=predicted_price
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
