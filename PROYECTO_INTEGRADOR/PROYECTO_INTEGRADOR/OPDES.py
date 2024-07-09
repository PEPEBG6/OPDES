from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from functools import wraps
import os
import hashlib
import base64

app = Flask(__name__, template_folder='templates')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'opdes'
app.secret_key = 'mysecrety'
bcrypt = Bcrypt(app)
mysql = MySQL(app)

#Ruta para logearse.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rol' not in session:
            flash('Debe iniciar sesión para acceder a esta página.')
            return redirect(url_for('Login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



#Ruta de roles.
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



#Ruta para almacenamiento de imagenes.
def save_photo(file):
    if file and file.filename:
        return file.read()
    return None

#Ruta de inicializacion.
@app.route('/')
def Inicio():
    return render_template('Inicio.html')



#Ruta de Login.
@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT ro.rol, contraseña FROM usuarios us INNER JOIN roles ro ON us.id_rol = ro.id WHERE us.correo = %s', (correo,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario:
            stored_password = usuario[1]
            if bcrypt.check_password_hash(stored_password, contraseña):
                session['correo'] = correo  
                session['rol'] = usuario[0]
                if usuario[0] == 'Publicador' or usuario[0] == 'Visualizador':
                    return redirect(url_for('Visualizador'))
                elif usuario[0] == 'Administrador':
                    return redirect(url_for('Administrador'))
                else:
                    flash('Rol no válido', 'error')
            else:
                flash('Correo o contraseña incorrectos', 'error')
        else:
            flash('Correo o contraseña incorrectos', 'error')

    return render_template('Login.html')



# Ruta de registro de usuario.
@app.route('/Registro')
def Registro():
    return render_template('Registrarse.html')


#Ruta para registrar usuario.
@app.route('/guardarRegistro', methods=['POST'])
def guardarRegistro():
    if request.method == 'POST':
        Vnombre = request.form['Nombre']
        Vapellidos = request.form['Apellidos']
        Vfecha_nac = request.form['Fecha_nac']
        Vcorreo = request.form['Correo']
        Vcontraseña = request.form['Contraseña']
        Vrol = int(request.form['rol'])

        hashed_password = bcrypt.generate_password_hash(Vcontraseña).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO usuarios (nombre, apellidos, f_nacimiento, correo, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s, %s)', 
                       (Vnombre, Vapellidos, Vfecha_nac, Vcorreo, hashed_password, Vrol))
        mysql.connection.commit()
        cursor.close()

        session['correo'] = Vcorreo
        if Vrol == 1:
            session['rol'] = 'Publicador'
        elif Vrol == 2:
            session['rol'] = 'Visualizador'

        if Vrol == 1 or Vrol == 2:
            return redirect(url_for('Visualizador'))
        else:
            flash('Error al registrar usuario', 'error')
            return redirect(url_for('Registrarse'))

    flash('Error al registrar usuario', 'error')
    return redirect(url_for('Registrarse'))



#Ruta de registro de proyectos.
@app.route('/Registro_Proyecto')
@login_required
def Registro_Proyecto():
    return render_template('Registro_Proyecto.html')



#Ruta para guardar proyecto.
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
        
        file = request.files.get('file-upload')
        if file and file.filename:
            imagen = file.read()
        else:
            flash('No file selected or file not allowed')
            return redirect(url_for('Registro_Proyecto'))

        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO proyectos (nombre, nombre_empresa, correo_electronico, telefono, foto, descripcion, objetivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (Vnombre, Vnombreempresa, Vcorreo, Vtelefono, imagen, Vdescripcion, Vobjetivo))
        mysql.connection.commit()

        
        id_proyecto = cursor.lastrowid

        
        cursor.execute('SELECT id FROM usuarios WHERE correo = %s', (session['correo'],))
        id_usuario = cursor.fetchone()[0]

        
        cursor.execute('''
            INSERT INTO proyectos_usuarios (id_usuario, id_proyecto)
            VALUES (%s, %s)
        ''', (id_usuario, id_proyecto))
        mysql.connection.commit()

        cursor.close()
        flash('Project saved successfully!')

    return redirect(url_for('VisualizadorProyectos'))



#Ruta de Inicio (¿Quienes somos?)
@app.route('/Visualizador')
@login_required
def Visualizador():
    return render_template('Visualizador.html')



#Ruta para ver los proyectos.
@app.route('/VisualizadorProyectos')
@login_required
def VisualizadorProyectos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM proyectos')
    proyectosBD = cursor.fetchall()
    cursor.close()

    proyectos = [
        {
            'id': p[0],
            'nombre': p[1],
            #'nombreempresa': p[2],
            #'correo': p[3],
            #'telefono': p[4],
            'imagen': base64.b64encode(p[5]).decode('utf-8') if p[5] else None,
            #'descripcion': p[6],
            #'objetivo': p[7]
        } for p in proyectosBD
    ]

    return render_template('VisualizadorProyectos.html', proyectos=proyectos)



#Ruta para ver detalles de proyectos.
@app.route('/VisualizadorMasProyectos/<int:proyecto_id>')
@login_required
def VisualizadorMasProyectos(proyecto_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM proyectos WHERE id = %s', (proyecto_id,))
    proyecto = cursor.fetchone()
    cursor.close()

    if proyecto:
        proyecto_detalle = {
            'id': proyecto[0],
            'nombre': proyecto[1],
            'nombreempresa': proyecto[2],
            'correo': proyecto[3],
            'telefono': proyecto[4],
            'imagen': base64.b64encode(proyecto[5]).decode('utf-8') if proyecto[5] else None,
            'descripcion': proyecto[6],
            'objetivo': proyecto[7]
        }
        return render_template('VisualizadorMasProyectos.html', proyecto=proyecto_detalle)
    else:
        # Aquí puedes manejar el caso cuando no se encuentra el proyecto con ese ID
        flash('Proyecto no encontrado.', 'error')
        return redirect(url_for('VisualizadorProyectos'))





#Ruta de Perfil
@app.route('/Perfil', methods=['GET', 'POST'])
@login_required
def Perfil():
    if 'correo' not in session:
        return redirect(url_for('Login'))

    user_email = session.get('correo')

    if request.method == 'POST':
        nombre = request.form['name']
        correo = request.form['email']
        
        foto_perfil = save_photo(request.files.get('profile-pic'))
        foto_portada = save_photo(request.files.get('cover-pic'))

        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE usuarios 
            SET nombre=%s, correo=%s
            WHERE correo=%s
        ''', (nombre, correo, user_email))
        
        # Verificar si ya existe una fila en perfiles_usuarios para el usuario actual
        cursor.execute('''
            SELECT id FROM perfiles_usuarios WHERE id_usuario=(SELECT id FROM usuarios WHERE correo=%s)
        ''', (user_email,))
        profile_user_exists = cursor.fetchone()

        # Si la fila existe, actualiza; si no, inserta una nueva fila
        if profile_user_exists:
            if foto_perfil:
                cursor.execute('''
                    UPDATE perfiles_usuarios 
                    SET foto_perfil=%s
                    WHERE id_usuario=(SELECT id FROM usuarios WHERE correo=%s)
                ''', (foto_perfil, user_email))
            
            if foto_portada:
                cursor.execute('''
                    UPDATE perfiles_usuarios 
                    SET foto_portada=%s
                    WHERE id_usuario=(SELECT id FROM usuarios WHERE correo=%s)
                ''', (foto_portada, user_email))
        else:
            cursor.execute('''
                INSERT INTO perfiles_usuarios (id_usuario, foto_perfil, foto_portada)
                VALUES ((SELECT id FROM usuarios WHERE correo=%s), %s, %s)
            ''', (user_email, foto_perfil, foto_portada))

        mysql.connection.commit()
        cursor.close()

        flash('Perfil actualizado exitosamente.')
        return redirect(url_for('Perfil'))

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT u.nombre, u.apellidos, u.correo, p.foto_perfil, p.foto_portada
        FROM usuarios u
        LEFT JOIN perfiles_usuarios p ON u.id = p.id_usuario
        WHERE u.correo = %s
    ''', (user_email,))
    user_data = cursor.fetchone()
    cursor.close()

    if not user_data:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('Login'))

    user_profile_data = {
        'nombre': user_data[0],
        'apellidos': user_data[1],
        'correo': user_data[2],
        'foto_perfil': base64.b64encode(user_data[3]).decode('utf-8') if user_data[3] else None,
        'foto_portada': base64.b64encode(user_data[4]).decode('utf-8') if user_data[4] else None
    }

    return render_template('perfil.html', user_data=user_profile_data)



#Ruta par ver mis proyectos.
@app.route('/Perfil_Proyectos')
@login_required
def Perfil_Proyectos():
    
    user_email = session.get('correo')

    
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT p.id, p.nombre, p.descripcion, p.objetivo, p.foto
        FROM proyectos p
        INNER JOIN proyectos_usuarios pu ON p.id = pu.id_proyecto
        INNER JOIN usuarios u ON pu.id_usuario = u.id
        WHERE u.correo = %s
    ''', (user_email,))
    proyectosBD = cursor.fetchall()
    cursor.close()

    
    proyectos = [
        {
            'id': p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'objetivo': p[3],
            'imagen': base64.b64encode(p[4]).decode('utf-8') if p[4] else None,
        } for p in proyectosBD
    ]

    return render_template('Perfil_Proyectos.html', proyectos=proyectos)



#Ruta para eliminar proyecto.
@app.route('/eliminarProyecto/<int:proyecto_id>', methods=['POST'])
@login_required
def eliminarProyecto(proyecto_id):
    user_email = session.get('correo')

    cursor = mysql.connection.cursor()
    cursor.execute('''
        DELETE p
        FROM proyectos p
        JOIN proyectos_usuarios pu ON p.id = pu.id_proyecto
        JOIN usuarios u ON pu.id_usuario = u.id
        WHERE p.id = %s AND u.correo = %s
    ''', (proyecto_id, user_email))
    mysql.connection.commit()
    cursor.close()
    return '', 204



#Ruta para editar proyecto.
#Ruta para editar proyecto.
@app.route('/editarProyecto/<int:proyecto_id>', methods=['GET', 'POST'])
@login_required
def editarProyecto(proyecto_id):
    user_email = session.get('correo')

    if request.method == 'POST':
        nombre = request.form['nombre-proyecto']
        nombreempresa = request.form['nombre-empresa']
        correo = request.form['correo-empresa']
        telefono = request.form['telefono-empresa']
        descripcion = request.form['descripcion-proyecto']
        objetivo = request.form['objetivo-proyecto']
        
        file = request.files.get('file-upload')
        imagen = file.read() if file and file.filename else None

        cursor = mysql.connection.cursor()
        
        if imagen:
            cursor.execute('''
                UPDATE proyectos p
                JOIN proyectos_usuarios pu ON p.id = pu.id_proyecto
                JOIN usuarios u ON pu.id_usuario = u.id
                SET p.nombre=%s, p.nombre_empresa=%s, p.correo_electronico=%s, p.telefono=%s, p.descripcion=%s, p.objetivo=%s, p.foto=%s
                WHERE p.id=%s AND u.correo=%s
            ''', (nombre, nombreempresa, correo, telefono, descripcion, objetivo, imagen, proyecto_id, user_email))
        else:
            cursor.execute('''
                UPDATE proyectos p
                JOIN proyectos_usuarios pu ON p.id = pu.id_proyecto
                JOIN usuarios u ON pu.id_usuario = u.id
                SET p.nombre=%s, p.nombre_empresa=%s, p.correo_electronico=%s, p.telefono=%s, p.descripcion=%s, p.objetivo=%s
                WHERE p.id=%s AND u.correo=%s
            ''', (nombre, nombreempresa, correo, telefono, descripcion, objetivo, proyecto_id, user_email))

        mysql.connection.commit()
        cursor.close()
        flash('Proyecto actualizado exitosamente.')
        return redirect(url_for('Perfil_Proyectos'))

    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT p.nombre, p.nombre_empresa, p.correo_electronico, p.telefono, p.descripcion, p.objetivo, p.foto
        FROM proyectos p
        JOIN proyectos_usuarios pu ON p.id = pu.id_proyecto
        JOIN usuarios u ON pu.id_usuario = u.id
        WHERE p.id = %s AND u.correo = %s
    ''', (proyecto_id, user_email))
    proyecto = cursor.fetchone()
    cursor.close()

    if not proyecto:
        flash('Proyecto no encontrado.', 'error')
        return redirect(url_for('Perfil_Proyectos'))

    proyecto_data = {
        'id': proyecto_id,
        'nombre': proyecto[0],
        'nombre_empresa': proyecto[1],
        'correo': proyecto[2],
        'telefono': proyecto[3],
        'descripcion': proyecto[4],
        'objetivo': proyecto[5],
        'imagen': base64.b64encode(proyecto[6]).decode('utf-8') if proyecto[6] else None
    }

    return render_template('editarProyecto.html', proyecto=proyecto_data)




#FALTANTES
@app.route('/VisualizadorNotificaciones')
@login_required
def VisualizadorNotificaciones():
    return render_template('VisualizadorNotificaciones.html')

@app.route('/Notificaciones')
@login_required
def Notificaciones():
    return render_template('Notificaciones.html')



@app.route('/CerrarSesion')
@login_required
def logout():
    session.clear()
    return redirect(url_for('Login'))

if __name__ == '__main__':
    app.run(debug=True)
