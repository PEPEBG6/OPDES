from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import hashlib

app= Flask(__name__,  template_folder='templates')
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='opdes'
app.secret_key= 'mysecrety'
Bcrypt=Bcrypt(app)
mysql= MySQL(app)


@app.route('/')
def Inicio():
    return render_template('Inicio.html')

#Esta es la ruta para ir a la vista para el registro de un proyecto 
@app.route('/Registro_Proyecto')
def Registro_Proyecto():
    return render_template('Registro_Proyecto.html')

#Esta es la ruta para guardar un proyecto en la base de datos
@app.route('/guardarProyecto', methods=['POST'])
def guardarProyecto():
    if 'rol' in session:
        if request.method == 'POST':
            Vnombre = request.form['nombre-proyecto']
            Vnombreempresa = request.form['nombre-empresa']
            Vcorreo = request.form['correo-empresa']
            Vtelefono = request.form['telefono-empresa']
            Vdescripcion = request.form['descripcion-proyecto']
            Vobjetivo = request.form['objetivo-proyecto']
            
            # Manejo del archivo de imagen
            if 'file-upload' not in request.files:
                return 'No file part'
            file = request.files['file-upload']
            if file.filename == '':
                return 'No selected file'
            if file:
                imagen = file.read()
            else:
                return 'File not allowed'

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO proyectos (nombre, nombreempresa, correo, telefono, imagen, descripcion, objetivo) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                        (Vnombre, Vnombreempresa, Vcorreo, Vtelefono, imagen, Vdescripcion, Vobjetivo))
            mysql.connection.commit()
            cursor.close()

        return redirect(url_for('VisualizadorProyectos'))
    else:
        return redirect(url_for('Login'))

#ESTA RUTA ES PARA ADMINISTRADOR 
@app.route('/Administrador')
def Administrador():
    return render_template('admin.html')

@app.route('/AdminProyectos')
def AdminProyectos():
    return render_template('adminProyectos.html')

@app.route('/AdminInicio')
def AdminInicio():
    return render_template('adminInicio.html')

#ESTA RUTA ES PARA EL ROL VISUALIZADOR DE PROYECTOS
@app.route('/Visualizador')
def Visualizador():
    return render_template('Visualizador.html')

@app.route('/Visualizadorperfil')
def VisualizadorPerfil():
    return render_template('VisualizadorPerfil.html')


@app.route('/VisualizadorProyectos')
def VisualizadorProyectos():
    if 'rol' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM proyectos')
        proyectos = cursor.fetchall()
        cursor.close()

        # Convierte las imágenes BLOB a base64 para poder ser renderizadas en HTML
        proyectos = [
            {
                'id': p[0],
                'nombre': p[1],
                'nombreempresa': p[2],
                'correo': p[3],
                'telefono': p[4],
                'imagen': p[5].decode('utf-8') if p[5] else None,
                'descripcion': p[6],
                'objetivo': p[7]
            } for p in proyectos
        ]

        return render_template('VisualizadorProyectos.html', proyectos=proyectos)
    else:
        return redirect(url_for('Login'))

    

@app.route('/VisualizadorNotificaciones')
def VisualizadorNotificaciones():
    return render_template('VisualizadorNotificaciones.html')

@app.route('/VisualizadorMasProyectos')
def VisualizadorMasProyectos():
    return render_template('VisualizadorMasProyectos.html')




@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_rol, contraseña FROM usuarios WHERE correo = %s', (correo,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario:
            stored_password = usuario[1]
            if Bcrypt.check_password_hash(stored_password, contraseña):
                session['rol'] = usuario[0]
                if usuario[0] == 1:
                    return redirect(url_for('Visualizador'))
                elif usuario[0] == 2:
                    return redirect(url_for('Visualizador'))
                elif usuario[0]== 3:
                    return redirect(url_for('Administrador'))
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

        
        hashed_password = Bcrypt.generate_password_hash(Vcontraseña).decode('utf-8')

        cs = mysql.connection.cursor()
        cs.execute('INSERT INTO usuarios (nombre, apellidos, f_nacimiento, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s, %s)', 
                   (Vnombre, Vapellidos, Vfecha_nac, Vcorreo, hashed_password, Vrol))
        mysql.connection.commit()

    return redirect(url_for('Registro'))






@app.route('/Inicio_pagina_Publicador')
def Inicio_pagina():
    return render_template('Inicio2.html')

@app.route('/Proyectos')
def Proyectos():
    return render_template('proyectos.html')

@app.route('/Perfil')
def Perfil():
    return render_template('perfil.html')

@app.route('/Notificaciones')
def Notificaciones():
    return render_template('Notificaciones.html')

@app.route('/PerfilProyecto')
def PerfilProyecto():
    return render_template('Proyectoperfil.html')


#Esta ruta es para la interfaz de proyectos de otras personas
@app.route('/Perfil_Proyectos')
def Perfil_Proyectos():
    return render_template('Perfil_Proyectos.html')

if __name__ == '__main__':
    app.run(debug=True)