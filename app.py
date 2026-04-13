import os
from flask import Flask, render_template, request, send_from_directory, abort
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps

app = Flask(__name__)

# Límite de 1MB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.bmp']
app.config['UPLOAD_PATH'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

def validate_image(stream):
    try:
        image = Image.open(stream)
        image.verify()
        stream.seek(0)

        format = image.format.lower()
        if format == 'jpeg':
            return '.jpg'

        return '.' + format
    except:
        return None

@app.errorhandler(413)
def too_large(e):
    return "El archivo excede 1MB", 413

@app.route('/')
def index():
    # Cargar archivos y dividirlos en las dos categorías
    archivos = os.listdir(app.config['UPLOAD_PATH'])
    bordered_files = [f for f in archivos if f.startswith('borde_')]
    original_files = [f for f in archivos if not f.startswith('borde_')]
    
    return render_template('index.html', original_files=original_files, bordered_files=bordered_files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    if filename != '':
        file_ext = os.path.splitext(filename)[1].lower()

        # Validación de formato y archivo corrupto
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_file.stream):
            return "Formato inválido o archivo corrupto", 400
        
        filepath = os.path.join(app.config['UPLOAD_PATH'], filename)

        # Validación de duplicado
        if os.path.exists(filepath):
            return "El archivo ya existe", 400

        # Guardar archivo original
        uploaded_file.save(filepath)
        print(f"Imagen '{filename}' subida correctamente.", flush=True)

        # Generar el borde
        bordered_filename = "borde_" + filename
        bordered_filepath = os.path.join(app.config['UPLOAD_PATH'], bordered_filename)
        
        with Image.open(filepath) as img:
            img_con_borde = ImageOps.expand(img, border=20, fill='black')
            img_con_borde.save(bordered_filepath)
        print(f"Borde agregado a '{filename}'.", flush=True)

    return '', 204

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)