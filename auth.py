from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# def save_users(users):
#     with open(USERS_FILE, 'w') as f:
#         json.dump(users, f)
