import os
import sqlite3
import cloudinary
import urllib.request  
from werkzeug.utils import secure_filename         
from flask import Flask, redirect, render_template,request, session, flash, url_for, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

UPLOAD_FOLDER = 'static/img'

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Formatos disponibles para imágenes
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
FORMATOS_DISPONIBLES = (['png', 'jpg', 'jpeg', 'gif'])

Session(app)



def formato_archivo(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in FORMATOS_DISPONIBLES

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
    

@app.route("/perfil", methods=[ "GET", "POST"])
def perfil():
    if request.method == "POST":
        if 'producto_imagen' not in request.files:
            flash("Error al subir archivo")
            return render_template("perfil.html")

        img = request.files['producto_imagen']

        if img and formato_archivo(img.filename):
            filename = secure_filename(img.filename)
            img.save(os.path.join(UPLOAD_FOLDER, filename))

            db = sqlite3.connect("matheno.db", check_same_thread=False)
            c = db.cursor()

            # Obtener el ID del usuario actual
            user_id = session["user_id"][0][0]

            # Actualizar la ruta de la imagen en la base de datos
            c.execute("UPDATE Usuarios SET Imagen = ? WHERE IdUsuarios = ?", [filename, user_id])

            db.commit()
            db.close()

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
    
    respuestas = c.execute("Select inciso.Subsection, Correctas.Respuesta, Incorrectas.Respuesta FROM QuizzCreado JOIN inciso ON QuizzCreado.IdQuizzCreado = inciso.IdQuizz JOIN Correctas ON Correctas.IdInciso = inciso.IdInciso JOIN Incorrectas ON inciso.IdInciso = Incorrectas.IdInciso WHERE QuizzCreado.IdQuizzCreado = 2 ORDER BY Incorrectas.Respuesta desc, Correctas.Respuesta asc").fetchall()
    v2 = ['Pregunta','Respuesta Correcta', 'Respuesta Incorrecta']
    answer = []
    
    for i in respuestas:
        for j in v2:
            a = dict(zip(v2,i))
        answer.append(a)
    print(answer)
        

    return render_template("repro.html", answer = answer)