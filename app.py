import os
from flask import Flask, render_template, request, send_from_directory
from rembg import remove
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    input_file = request.files['image']
    bg_file = request.files.get('background')

    if not input_file:
        return "No image uploaded", 400

    # Save uploaded image
    input_path = os.path.join(UPLOAD_FOLDER, 'input.png')
    input_file.save(input_path)

    # Remove background
    input_image = Image.open(input_path)
    fg_image = remove(input_image).convert("RGBA")

    # Handle background
    if bg_file and bg_file.filename:
        bg_path = os.path.join(UPLOAD_FOLDER, 'bg.png')
        bg_file.save(bg_path)
        bg_image = Image.open(bg_path).convert("RGBA")
        bg_image = bg_image.resize(fg_image.size)
    else:
        # default solid color (white)
        bg_image = Image.new("RGBA", fg_image.size, (255, 255, 255, 255))

    # Combine
    final_image = Image.alpha_composite(bg_image, fg_image)
    output_path = os.path.join(UPLOAD_FOLDER, 'output.png')
    final_image.save(output_path)

    return render_template('index.html',
                           input_image='uploads/input.png',
                           output_image='uploads/output.png')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)