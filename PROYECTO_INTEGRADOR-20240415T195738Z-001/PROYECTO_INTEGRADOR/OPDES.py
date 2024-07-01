from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from functools import wraps
import hashlib
import base64

app= Flask(__name__,  template_folder='templates')
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='opdes'
app.secret_key= 'mysecrety'
Bcrypt=Bcrypt(app)
mysql= MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session:
            flash('Debe iniciar sesión para acceder a esta página.')
            return redirect(url_for('Login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles:
                flash('No tienes permisos para acceder a esta página.')
                return redirect(request.referrer or url_for('Login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def Inicio():
    return render_template('Inicio.html')


#Esta es la ruta para ir a la vista para el registro de un proyecto 
@app.route('/Registro_Proyecto')
@login_required
def Registro_Proyecto():
    
    return render_template('Registro_Proyecto.html')


#Esta es la ruta para guardar un proyecto en la base de datos
@app.route('/guardarProyecto', methods=['POST'])
@login_required
def guardarProyecto():
    
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
        cursor.execute('INSERT INTO proyectos (nombre, nombre_empresa, correo_electronico, telefono, foto, descripcion, objetivo) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                    (Vnombre, Vnombreempresa, Vcorreo, Vtelefono, imagen, Vdescripcion, Vobjetivo))
        mysql.connection.commit()
        cursor.close()

    return redirect(url_for('VisualizadorProyectos'))


#ESTA RUTA ES PARA ADMINISTRADOR 
@app.route('/Administrador')
@login_required
def Administrador():
    return render_template('admin.html')


@app.route('/AdminProyectos')
@login_required
def AdminProyectos():

    return render_template('adminProyectos.html')


@app.route('/AdminInicio')
@login_required
def AdminInicio():
    
    return render_template('adminInicio.html')


#ESTA RUTA ES PARA EL ROL VISUALIZADOR DE PROYECTOS
@app.route('/Visualizador')
@login_required
def Visualizador():
    
    return render_template('Visualizador.html')


@app.route('/Visualizadorperfil')
@login_required
def VisualizadorPerfil():
    
    return render_template('VisualizadorPerfil.html')



@app.route('/VisualizadorProyectos')
@login_required
def VisualizadorProyectos():

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM proyectos')
    proyectosBD = cursor.fetchall()
    cursor.close()

    # Convierte las imágenes BLOB a base64 para poder ser renderizadas en HTML
    proyectos = [
        {
            'id': p[0],
            'nombre': p[1],
            'nombreempresa': p[2],
            'correo': p[3],
            'telefono': p[4],
            'imagen': base64.b64encode(p[5]).decode('utf-8') if p[5] else None,
            'descripcion': p[6],
            'objetivo': p[7]
        } for p in proyectosBD
    ]

    return render_template('VisualizadorProyectos.html', proyectos=proyectos)

    

@app.route('/VisualizadorNotificaciones')
@login_required
def VisualizadorNotificaciones():
    
    return render_template('VisualizadorNotificaciones.html')



@app.route('/VisualizadorMasProyectos')
@login_required
def VisualizadorMasProyectos():
    
    return render_template('VisualizadorMasProyectos.html')



@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT ro.rol, contraseña FROM usuarios us inner join roles ro on us.id_rol = ro.id WHERE us.correo = %s', (correo,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario:
            stored_password = usuario[1]
            if Bcrypt.check_password_hash(stored_password, contraseña):
                session['rol'] = usuario[0]
                if usuario[0] == 'Publicador' or usuario[0] == 'Visualizador':
                    return redirect(url_for('Visualizador'))
                elif usuario[0] == 'Administrador':
                    return redirect(url_for('Administrador'))
                else:
                    flash('Rol no válido', 'error')
                    return redirect(url_for('Login'))
            else:
                flash('Correo o contraseña incorrectos', 'error')  # Cambia la categoría a 'error'
                return redirect(url_for('Login'))  
            
        else:
            flash('Correo o contraseña incorrectos', 'error')  # Cambia la categoría a 'error'
            return redirect(url_for('Login'))  

    return render_template('Login.html')





@app.route('/Registro')
def Registro ():
    return render_template('Registrarse.html')

@app.route('/guardarRegistro', methods=['POST'])
def guardarRegistro():
    if request.method == 'POST':
        Vnombre = request.form['Nombre']
        Vapellidos = request.form['Apellidos']
        Vfecha_nac = request.form['Fecha_nac']
        Vcorreo = request.form['Correo']
        Vcontraseña = request.form['Contraseña']
        Vrol = int(request.form['rol'])  # Asegúrate de convertir a entero

        hashed_password = Bcrypt.generate_password_hash(Vcontraseña).decode('utf-8')

        cs = mysql.connection.cursor()
        cs.execute('INSERT INTO usuarios (nombre, apellidos, f_nacimiento, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s, %s)', 
                   (Vnombre, Vapellidos, Vfecha_nac, Vcorreo, hashed_password, Vrol))
        mysql.connection.commit()
        cs.close()
        session['rol'] = Vrol
        
        # Redirige según el rol
        if Vrol == 1 or Vrol == 2:
            return redirect(url_for('Visualizador'))
        else:
            flash('Error al registrar usuario', 'error')
            return redirect(url_for('Registro'))
    
    # Manejo del caso en que el método no sea POST
    flash('Error al registrar usuario', 'error')
    return redirect(url_for('Registro'))







@app.route('/Inicio_pagina_Publicador')
@login_required
def Inicio_pagina():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('Inicio2.html')

@app.route('/Proyectos')
@login_required
def Proyectos():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('proyectos.html')

@app.route('/Perfil')
@login_required
def Perfil():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('perfil.html')

@app.route('/Notificaciones')
@login_required
def Notificaciones():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('Notificaciones.html')

@app.route('/PerfilProyecto')
@login_required
def PerfilProyecto():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('Proyectoperfil.html')


#Esta ruta es para la interfaz de proyectos de otras personas
@app.route('/Perfil_Proyectos')
@login_required
def Perfil_Proyectos():
    if 'rol' not in session: 
        return redirect(url_for('Login'))
    return render_template('Perfil_Proyectos.html')

@app.route('/CerrarSesion')
@login_required
def logout():
    session.clear()
    return redirect(url_for('Login'))


if __name__ == '__main__':
    app.run(debug=True)