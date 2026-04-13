import os
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageOps

app = Flask(__name__)

# Configuración de la carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    original_img = None
    bordered_img = None
    
    if request.method == 'POST':
        try:
            # Recibir el archivo desde el formulario HTML
            file = request.files.get('file')
            
            if file and file.filename != '':
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Guardar la imagen original en el servidor
                file.save(filepath)
                
                # Log para la consola de Render
                print(f"Imagen '{filename}' subida desde la web.", flush=True)

                # Procesar la imagen para agregar el borde negro
                bordered_filename = "borde_" + filename
                bordered_filepath = os.path.join(app.config['UPLOAD_FOLDER'], bordered_filename)
                
                with Image.open(filepath) as img:
                    # Agrega un borde negro de 20 píxeles
                    img_con_borde = ImageOps.expand(img, border=20, fill='black')
                    img_con_borde.save(bordered_filepath)
                
                # Log para la consola de Render
                print(f"Borde agregado a '{filename}' correctamente.", flush=True)
                
                original_img = filename
                bordered_img = bordered_filename

        except Exception as e:
            # Log en caso de error
            print(f"Error procesando la imagen: {e}", flush=True)

    return render_template('index.html', original_img=original_img, bordered_img=bordered_img)

# Ruta para que el navegador pueda mostrar las imágenes de la carpeta 'uploads'
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)