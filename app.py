import os
import sqlite3

from flask import Flask, redirect, render_template,request, session, flash, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=[ "GET", "POST"])
def register():
    session.clear()
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    if request.method == "POST":
        if not request.form.get("Usuario"):
            flash("must provide username")
            return render_template("register.html")
        elif not request.form.get("Password"):
            flash("must provide password")
            return render_template("register.html")
        elif not request.form.get("confirmation"):
            flash("must confirm password")
            return render_template("register.html")
        elif request.form.get("Password") != request.form.get("confirmation"):
            flash("passwords must match")
            return render_template("register.html")
        elif len(request.form.get("Password")) < 8:
            flash("password must be at least 8 characters")
            return render_template("register.html")
        elif request.form.get("Password").isalpha():
            flash("password must contain at least one number or symbol")
            return render_template("register.html")
        elif request.form.get("Password").isdigit():
            flash("password must contain at least one letter or symbol")
            return render_template("register.html")

        search = c.execute("SELECT * FROM Usuarios WHERE Usuario = ?", [request.form.get("Usuario")]).fetchall()
        if len(search) != 0:
            flash("username already taken")
            return render_template("register.html")
        c.execute("INSERT INTO Usuarios (Usuario, Email, Password) VALUES (?, ?, ?)", [request.form.get("Usuario"), request.form.get("Email"), generate_password_hash(request.form.get("Password"))])

        remember = db.execute("SELECT IdUsuarios FROM Usuarios WHERE Usuario = ?", [request.form.get("Usuario")]).fetchall()
        session["user_id"] = [remember[0], ["IdUsuarios"]]
        db.commit()
        db.close()

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    if request.method == "POST":
        if not request.form.get("Usuario"):
            flash('must provide username')
            return render_template("login.html")
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")
        
        search = db.execute("SELECT * FROM Usuarios WHERE Usuario = ?", [request.form.get("Usuario")]).fetchall()

        if len(search) == 0:
            flash("invalid username")
            return render_template("login.html")
        elif not check_password_hash(search[0][3], request.form.get("password")):
            flash("invalid password")
            return render_template("login.html")
        
        remember = db.execute("SELECT IdUsuarios FROM Usuarios WHERE Usuario = ?", [request.form.get("Usuario")]).fetchall()
        session["user_id"] = [remember[0], ["IdUsuarios"]]
        db.commit()
        db.close()
        return redirect("/")
    
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/create_quizz", methods=[ "GET", "POST"])
@login_required
def create_quizz():
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    if request.method == "POST":
        Nombre = request.form.get("Nombre")
        Descripcion = request.form.get("Descripcion")
        Categoria  = request.form.get("Categoria")
        if not Nombre:
            flash("Se tiene que ingresar un nombre para el nuevo quizz.")
            return render_template("create_quizz.html")
        
        return render_template("create_quizz.html", Nombre = Nombre)
    else:
        return render_template("create_quizz.html")