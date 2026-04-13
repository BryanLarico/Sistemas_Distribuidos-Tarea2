import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.bmp', '.png']
app.config['UPLOAD_PATH'] = 'uploads'

# Aseguramos que la carpeta uploads exista
os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)

def validate_image(stream):
    try:
        image = Image.open(stream)
        image.verify()
        stream.seek(0)

        format = image.format.lower()
        if format == 'jpeg':
            return '.jpg'
        if format == 'bmp':
            return '.bmp'

        return '.' + format
    except Exception as e:
        return None

# Excepciones de control
@app.errorhandler(413)
def too_large(e):
    return "Error: El archivo es demasiado grande (Máximo 5MB).", 413

@app.errorhandler(404)
def not_found(e):
    return "Error: Recurso no encontrado.", 404

@app.route('/', methods=['GET', 'POST'])
def index():
    original_img = None
    bordered_img = None
    error_msg = None

    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return "Error: No se encontró el archivo en la petición", 400
            
            uploaded_file = request.files['file']
            filename = secure_filename(uploaded_file.filename)

            if filename != '':
                file_ext = os.path.splitext(filename)[1].lower()

                # Validación de extensión
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return f"Error: Extensión no permitida. Solo {app.config['UPLOAD_EXTENSIONS']}", 400
                
                # Validación de contenido real de la imagen
                ext_validada = validate_image(uploaded_file.stream)
                
                # Permite que .jpeg y .jpg se consideren compatibles
                if file_ext != ext_validada and not (file_ext == '.jpeg' and ext_validada == '.jpg'):
                    return "Error: El archivo está corrupto o no es una imagen válida", 400
                    
                # Nombres de ruta
                filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
                bordered_filename = "borde_" + filename
                bordered_filepath = os.path.join(app.config['UPLOAD_PATH'], bordered_filename)

                # 1. Guardar la imagen
                uploaded_file.save(filepath)
                original_img = filename

                # 2. Agregar borde en el servidor (Python)
                with Image.open(filepath) as img:
                    # Agregae un borde negro de 20 píxeles
                    img_con_borde = ImageOps.expand(img, border=20, fill='black')
                    img_con_borde.save(bordered_filepath)
                
                bordered_img = bordered_filename

        except Exception as e:
            # Control de excepción general de procesamiento
            return f"Ocurrió un error en el servidor al procesar la imagen: {str(e)}", 500

    # 3. Exhibir imágenes(2) sin/con bordes en cliente
    return render_template('index.html', original_img=original_img, bordered_img=bordered_img)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)