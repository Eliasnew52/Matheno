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
        Dificultad = request.form.get("Dificultad")
        Autor = session["user_id"][0][0]
        if not Nombre:
            flash("Se tiene que ingresar un nombre para el nuevo quizz.")
            return render_template("create_quizz.html")
        elif not Categoria:
            flash("Se tiene que ingresar una categoria para el nuevo quizz.")
            return render_template("create_quizz.html")
        elif not Dificultad:
            flash("Se tiene que ingresar una dificultad para el nuevo quizz.")
            return render_template("create_quizz.html")
        
        search = c.execute("SELECT * FROM QuizzCreado WHERE Quizz = ?", [Nombre]).fetchall()
        if len(search) != 0:
            flash("El quizz ya existe.")
            return render_template("create_quizz.html")
        c.execute("INSERT INTO QuizzCreado (Quizz, Descripcion, IdCategoria, IdDificultad, IdAutor) VALUES (?, ?, ?, ?, ?)", [Nombre, Descripcion, Categoria, Dificultad, Autor])
        return render_template("construct.html")
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
    
    quizz = c.execute("SELECT QuizzCreado.Quizz, QuizzCreado.Descripcion, QuizzCreado.PortadaLink, QuizzCreado.Verificado, Categoria.Categoria, Dificultad.Dificultad FROM QuizzCreado JOIN Categoria ON Categoria.IdCategoria = QuizzCreado.IdCategoria JOIN Dificultad ON Dificultad.IdDificultad = QuizzCreado.IdDificultad WHERE QuizzCreado.IdQuizzCreado = 2").fetchall()    
    r = []
    print(quizz[0])
       
    for i in quizz:
        print(i)
        dic = {
            "Quizz": i[0],
            "Descripcion": i[1],
            "PortadaLink": i[2],
            "Verificado": i[3],
            "Categoria": i[4],
            "Dificultad": i[5],
        }
        r.append(dic) 
    
    return render_template("quizz.html" , r = r)


@app.route("/repro", methods=["GET", "POST"])
def repro():
    db = sqlite3.connect("matheno.db", check_same_thread=False)
    c = db.cursor()
    count = 0
    id_preguntas = c.execute("Select inciso.IdInciso, inciso.Subsection from inciso WHERE inciso.IdQuizz = 2").fetchall()
   # print(id_preguntas)
    preguntas_list = []
    
    for i in id_preguntas:
        print("aaa",i[0])
        
        respuestas = c.execute("select Respuestas.Respuesta, Respuestas.Verificacion from Respuestas JOIN inciso ON inciso.IdInciso = Respuestas.IdInciso WHERE inciso.IdInciso = ?", str(i[0])).fetchall()
       # print(respuestas)
        pregunta_dic = {
            "id_preg": i[0],
            "preg": i[1],
            "respuestas": respuestas,
        }
        preguntas_list.append(pregunta_dic)

        search = c.execute("SELECT * FROM QuizzJugado WHERE IdQuizz = 2 AND IdUsuarios = 2").fetchall()
        if len(search) == 0:     
            c.execute("INSERT INTO QuizzJugado (IdQuizz, IdUsuarios) VALUES (2, 2)") 
            c.execute("INSERT INTO Puntaje (Puntaje, IdQuizzJugado) VALUES (0,1)")
        
    if request.method == "POST":
        
        data = request.get_json()
        pregunta_id = data.get('preguntaId')
        respuesta = data.get('respuesta')
        #print(pregunta_id, respuesta)
        
        verificar_respuesta = c.execute("SELECT Respuestas.Verificacion  FROM Respuestas JOIN inciso ON inciso.IdInciso = Respuestas.IdInciso WHERE inciso.IdInciso = ? AND Respuestas.Respuesta = ?", [pregunta_id, respuesta]).fetchall()
        #print(verificar_respuesta)
        for i in verificar_respuesta:
            print(i[0])
            if i[0] == "correcta":
            
                c.execute("UPDATE Puntaje SET Puntaje = Puntaje + 1 WHERE IdQuizzJugado  = 1")
        print(count)
        
        db.commit()
        db.close()
        return render_template("repro.html", p=pregunta_id, r=respuesta)

    else:
        return render_template("repro.html", p=preguntas_list)
    



    
@app.route("/construct", methods=["GET", "POST"] )
def construct():
    
    if request.method == "POST":
        preguntas_respuestas = []

        # Obtener las claves del formulario que comienzan con 'Pregunta'
        claves_preguntas = [clave for clave in request.form if clave.startswith('Pregunta')]

        # Recorrer las claves y obtener el valor correspondiente (las preguntas y sus respuestas)
        for clave in claves_preguntas:
            pregunta = request.form[clave]

            # Obtener el nombre de la clave de respuesta asociada a esta pregunta
            clave_respuesta = 'Respuesta' + clave[8:]  # Asumiendo que las respuestas tienen el formato 'Respuesta1', 'Respuesta2', etc.

            if clave_respuesta in request.form:
                respuesta = request.form[clave_respuesta]
            else:
                respuesta = None  # Puedes manejar esto según tu lógica

            # Crear un diccionario con la pregunta y su respuesta (si está presente)
            pregunta_respuesta = {'pregunta': pregunta, 'respuesta': respuesta}
            preguntas_respuestas.append(pregunta_respuesta)

        # Imprimir o hacer algo con la lista de diccionarios de preguntas y respuestas
        print('Lista de preguntas y respuestas:', preguntas_respuestas)
    
        return render_template("inicio.html")
    else:
        return render_template("construct.html")

