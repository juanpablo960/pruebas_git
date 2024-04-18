from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

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

if __name__ == '__main__':
    app.run(debug=True)