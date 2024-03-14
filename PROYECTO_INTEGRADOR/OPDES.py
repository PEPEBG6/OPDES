from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app= Flask(__name__,  template_folder='templates')


@app.route('/')
def Inicio():
    return render_template('Inicio.html')

@app.route('/Login')
def Login():
    return render_template('Login.html')

@app.route('/Registro')
def Registro ():
    return render_template('Registrarse.html')

@app.route('/Inicio_pagina')
def Inicio_pagina():
    return render_template('Inicio2.html')

if __name__ == '__main__':
    app.run(debug=True)