from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import hashlib

app= Flask(__name__,  template_folder='templates')
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='opdes'
app.secret_key= 'mysecrety'
bcrypt = Bcrypt(app)
mysql= MySQL(app)


@app.route('/')
def Inicio():
    return render_template('Inicio.html')

@app.route('/Admin')  #Se creo rurta Administrador
def Admin ():
    return render_template('Admin.html')

@app.route('/Visualizador') #Se creo ruta de Visualizador
def Visualizador ():
    return render_template('Visualizador.html')


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_rol, contraseña FROM usuarios WHERE correo = %s', (correo,))
        usuario = cursor.fetchone()

        if usuario:
            stored_password = usuario[1]
            if bcrypt.check_password_hash(stored_password, contraseña):
                session['rol'] = usuario[0]
                if usuario[0] == 1:
                    return redirect(url_for('Admin'))
                elif usuario[0] == 2:
                    return redirect(url_for('Visualizador'))
            else:
                flash('Correo o contraseña incorrectos')
                return render_template('Login.html')  
            
        else:
            flash('Correo o contraseña incorrectos')
            return render_template('Login.html')  

    return render_template('Login.html')



    


@app.route('/Registro')
def Registro ():
    return render_template('Registrarse.html')

@app.route('/guardarRegistro', methods=['POST'])
def guardarRegistro():
    if request.method == 'POST':
        Vnombre=request.form['Nombre']
        Vapellidos=request.form['Apellidos']
        Vfecha_nac=request.form['Fecha_nac']
        Vcorreo=request.form['Correo']
        Vcontraseña=request.form['Contraseña']
        Vrol=request.form['rol']

        
        hashed_password = bcrypt.generate_password_hash(Vcontraseña).decode('utf-8')

        cs = mysql.connection.cursor()
        cs.execute('INSERT INTO usuarios (nombre, apellidos, f_nacimiento, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s, %s)', 
                   (Vnombre, Vapellidos, Vfecha_nac, Vcorreo, hashed_password, Vrol))
        mysql.connection.commit()

    return redirect(url_for('Registro'))



@app.route('/Inicio_pagina')
def Inicio_pagina():
    return render_template('Inicio2.html')

@app.route('/Proyectos')
def Proyectos():
    return render_template('proyectos.html')

@app.route('/Perfil')
def Perfil():
    return render_template('perfil.html')

if __name__ == '__main__':
    app.run(debug=True)