from flask import Flask, render_template,request
from cs50 import SQL
app = Flask(__name__)

db = SQL("sqlite///matheno.db")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register.html')
def register():
    user = request.args.post('user')
    email = request.args.post('email')
    password = request.args.post('password')
    return render_template('register.html')

@app.route('')
def login():
    email = request.args.post('email')
    password = request.args.post('password')
    return render_template('login.html')

@app.route('/users/<string:user>', methods=['POST'])
def user():
    return render_template('user.html', user=user)