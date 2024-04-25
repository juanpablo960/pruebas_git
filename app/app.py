# Importar los módulos necesarios
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'campus_alalay'
mysql = MySQL(app)

# Configuración de la carpeta para subir archivos
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'static', 'uploads'))
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga de archivos de video
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No se encontró el archivo'
    file = request.files['file']
    if file.filename == '':
        return 'No se seleccionó ningún archivo'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Guardar los datos del archivo en la base de datos MySQL
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO videos (filename) VALUES (%s)", (filename,))
        mysql.connection.commit()
        cur.close()
        return 'Datos del archivo guardados en la base de datos exitosamente'
    else:
        return 'Tipo de archivo no permitido'

# Ruta para mostrar los videos almacenados
@app.route('/ver_videos')
def ver_videos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM videos")
    videos_data = cur.fetchall()
    cur.close()
    
    # Crear una lista de diccionarios con los datos de los videos
    videos = [{'filename': str(video[0])} for video in videos_data]

    return render_template('ver_videos.html', videos=videos)

# Ruta y función para manejar el registro de docentes
@app.route('/registrar_docente', methods=['GET', 'POST'])
def registrar_docente():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_completo = request.form['nombre']
        correo_electronico = request.form['email']
        contrasena = request.form['contrasena']
        especialidad = request.form['especialidad']
        nacionalidad = request.form['nacionalidad']
        foto = request.files['foto']
        descripcion = request.form['descripcion']

        # Guardar la foto en la carpeta de subidas
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None  # Opcional: si no se sube ninguna foto

        # Insertar los datos en la base de datos
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO registro_docentes (nombre_completo, correo_electronico, contrasena, especialidad, nacionalidad, foto, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (nombre_completo, correo_electronico, contrasena, especialidad, nacionalidad, filename, descripcion))
            mysql.connection.commit()
            cur.close()
            # Si todo sale bien, establecer el mensaje de éxito
            flash("Docente registrado exitosamente.", "success")
            return redirect(url_for('registrar_docente'))
        except Exception as e:
            # Si ocurre un error, establecer el mensaje de error
            flash("Error al registrar el docente.", "error")

    return render_template('registro_docente.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'  # Clave secreta para el paquete flash
    app.run(debug=True)