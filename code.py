from flask import Flask, request, render_template, send_file, jsonify
from rembg import remove
from PIL import Image, ImageOps
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-background', methods=['POST'])
def remove_background():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        input_image = Image.open(file).convert("RGBA")
        output_image = remove(input_image)

        img_bytes = io.BytesIO()
        output_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/add-background', methods=['POST'])
def add_background():
    try:
        file = request.files['file']
        removed_image = remove(Image.open(file).convert("RGBA"))

        bg_type = request.form.get("bg_type")
        if bg_type == 'color':
            color = request.form.get("bg_color", "#ffffff")
            background = Image.new("RGBA", removed_image.size, color)
        elif bg_type == 'image':
            bg_image = Image.open(request.files['bg_image']).convert("RGBA")
            background = bg_image.resize(removed_image.size)
        else:
            return jsonify({'error': 'Invalid background type'}), 400

        final = Image.alpha_composite(background, removed_image)
        img_bytes = io.BytesIO()
        final.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return send_file(img_bytes, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': f'Background add failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
