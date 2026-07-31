from flask import Flask, render_template, request, jsonify
from flask_login import (
	LoginManager,
	UserMixin,
	login_user,
	login_required,
	logout_user,
	current_user
)
from passlib.hash import sha512_crypt
import docker, psycopg

app = Flask(__name__)
app.secret_key = "secretgoeshere"

# Postgres database connection
conn = psycopg.connect(database="quarantine_db", user="postgres", password="root", host="localhost", port="5432")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS emails(id SERIAL PRIMARY KEY, sender TEXT NOT NULL, datetime TIMESTAMPTZ, text TEXT NOT NULL);")

# Instantiate login manager
login_manager = LoginManager()
login_manager.init_app(app)

# This location is specific to our dev deployment; it needs to be changed in other configurations and for prod
USER_FILE = "/home/jmcrae/docker-mailserver/docker-data/dms/config/postfix-accounts.cf"

class User(UserMixin):
	def __init__(self, email):
		self.id = email

# Function for reading user credentials into a dictionary
def load_users():
	users = {}
	with open(USER_FILE) as f:
		for line in f:
			line = line.strip()
			if not line:
				continue
			email, password_hash = line.split("|", 1)
			# remove Dovecot prefix
			if password_hash.startswith("{SHA512-CRYPT}"):
				password_hash = password_hash[len("{SHA512-CRYPT}"):]
			users[email] = password_hash
	return users

@login_manager.user_loader

# Function for authenticating user credentials
def load_user(user_id):
	users = load_users()
	if user_id in users:
		return User(user_id)
	return None

# Authentication API
@app.route("/api/login", methods=["POST"])
def login():
	data = request.get_json()

	email = data.get("email", "")
	password = data.get("password", "")

	users = load_users()

	if email not in users:
		return jsonify({"success": False}), 401

	stored_hash = users[email]

	if sha512_crypt.verify(password, stored_hash):
		login_user(User(email))
		return jsonify({"success": True})

	return jsonify({"success": False}), 401

# Quarantine fetch API
@app.route("/api/quarantine", methods=["POST"])
def quarantine():
	client = docker.from_env()
	container = client.containers.get("mailserver")
	

# Index page route
@app.route("/")
def index():
	return render_template("index.html")

# Login page route
@app.route("/login")
def login_page():
	return render_template("login.html")

# Dashboard page route
@app.route("/dashboard")
@login_required
def dashboard():
	return render_template("dashboard.html")

# Login confirmation page route
@app.route("/protected-login")
@login_required
def protected():
	return render_template("protected_login.html")

# Logout confirmation page route
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return render_template("logout.html")

# Quarantine page route
@app.route("/quarantine")
@login_required
def quarantine():
	return render_template("quarantine.html")

if __name__ == "__main__":
	app.run(debug=True)