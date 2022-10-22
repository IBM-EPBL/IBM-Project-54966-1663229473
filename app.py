from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello"


@app.route("/login")  # User Login
def login_page():
    return render_template("User/login.html")


if __name__ == "__main__":
    app.run(debug=True)
