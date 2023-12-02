import os
import sqlite3
import cloudinary
          
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
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    if request.method == "POST":
        if request.form.get("opc1") == "Buscar":
            Buscar = request.form.get("Buscar")
            return render_template("index.html", Buscar=Buscar)
    else:
        return render_template("index.html")

@app.route("/presentacion")
def presentacion():
    return render_template("presentacion.html")

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
        
        remember = db.execute("SELECT IdUsuarios,Usuario FROM Usuarios WHERE Usuario = ?", [request.form.get("Usuario")]).fetchall()
        print(remember)
        session["user_id"] = [remember[0], ["IdUsuarios"]]
        session["name"]=remember[0][1]
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
    
    Dificultad = c.execute("SELECT Dificultad FROM Dificultad").fetchall()
    if request.method == "POST":
        Nombre = request.form.get("Nombre")
        Descripcion = request.form.get("Descripcion")
        Categoria  = request.form.get("Categoria")
        if not Nombre:
            flash("Se tiene que ingresar un nombre para el nuevo quizz.")
            return render_template("create_quizz.html")
        
        return render_template("create_quizz.html", Nombre = Nombre, Dificultad=Dificultad)
    else:
        return render_template("create_quizz.html")
    
@app.route("/perfil")
def perfil():
    return render_template("perfil.html")
    
@app.route("/Buscar")
def Buscar():
    return render_template("buscar.html")

@app.route("/quizz")
def quizz():
    
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    
    view = c.execute("SELECT QuizzCreado.Quizz, QuizzCreado.Descripcion, QuizzCreado.PortadaLink, QuizzCreado.Verificado, Categoria.Categoria, Dificultad.Dificultad FROM QuizzCreado JOIN Categoria ON Categoria.IdCategoria = QuizzCreado.IdCategoria JOIN Dificultad ON Dificultad.IdDificultad = QuizzCreado.IdDificultad WHERE QuizzCreado.IdQuizzCreado = 2").fetchall()
    v = ["Quizz","Descripcion","Portada","Verificado","Categoria","Dificultad"]
    
    r = []
    for i in view:
        for j in v:
            a = dict(zip(v,i))
        r.append(a)
        
    play = c.execute("select IdQuizzCreado from QuizzCreado Where IdQuizzCreado = 1")
    
    return render_template("quizz.html" , r = r)


@app.route("/repro")
def repro():
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()

    id_preguntas = c.execute("Select inciso.IdInciso, inciso.Subsection from inciso WHERE inciso.IdQuizz = 2").fetchall()
    print(id_preguntas)
    preguntas_list = []
    
    for i in id_preguntas:
        print("aaa",i[0])
        
        respuestas = c.execute("select Respuestas.Respuesta, Respuestas.Verificacion from Respuestas JOIN inciso ON inciso.IdInciso = Respuestas.IdInciso WHERE inciso.IdInciso = ?", str(i[0])).fetchall()
        print(respuestas)
        pregunta_dic = {
            "id_preg": i[0],
            "preg": i[1],
            "respuestas": respuestas,
        }
        
        preguntas_list.append(pregunta_dic)
        
    return render_template("repro.html", p=preguntas_list)