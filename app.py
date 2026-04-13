import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from PIL import Image, ImageOps

app = Flask(__name__)

# Configuración de la carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    # Leer todos los archivos actuales en la carpeta uploads
    todos_los_archivos = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # Separar en dos listas: originales y con borde
    bordered_files = [f for f in todos_los_archivos if f.startswith('borde_')]
    original_files = [f for f in todos_los_archivos if not f.startswith('borde_')]
    
    return render_template('index.html', original_files=original_files, bordered_files=bordered_files)

@app.route('/upload_files', methods=['POST'])
def upload_files():
    # Esta ruta solo recibe los archivos de Dropzone
    file = request.files.get('file')
    
    if file and file.filename != '':
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Lógica para evitar duplicados
        if not os.path.exists(filepath):
            # Guardar la imagen original
            file.save(filepath)
            print(f"Imagen '{filename}' subida y guardada.", flush=True)

            # Procesar la imagen para agregar el borde negro
            bordered_filename = "borde_" + filename
            bordered_filepath = os.path.join(app.config['UPLOAD_FOLDER'], bordered_filename)
            
            with Image.open(filepath) as img:
                img_con_borde = ImageOps.expand(img, border=20, fill='black')
                img_con_borde.save(bordered_filepath)
            
            print(f"Borde agregado a '{filename}' correctamente.", flush=True)
        else:
            print(f"La imagen '{filename}' ya existe. Omitiendo.", flush=True)

    # Dropzone espera una respuesta JSON para saber que terminó
    return jsonify({'success': True})

# Ruta para que el navegador pueda mostrar las imágenes
@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)