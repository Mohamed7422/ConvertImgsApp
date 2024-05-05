import os
import zipfile

from flask import Flask, request, send_file, after_this_request
from PIL import Image
import io

# Create instance of Flask class
app = Flask(__name__)


@app.route('/')
def index():
    return '''
        <form method="post" action="/upload" enctype="multipart/form-data">
          <input type="file" name="images" multiple>
          <input type="submit">
        </form>
        '''


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('images')
    if not files:
        return "No files uploaded", 400

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as temp_zip:
        for index, file in enumerate(files):
            if file:
                try:
                    image = Image.open(file.stream)
                    img_io = io.BytesIO()
                    image.save(img_io, 'PNG', quality=70)
                    img_io.seek(0)
                    name, ext = os.path.splitext(file.filename)
                    temp_zip.writestr(f"{name}.png", img_io.getvalue())
                except Exception as e:
                    app.logger.error(f"Failed to process {file.filename}: {e}")

    zip_io.seek(0)

    # @after_this_request
    # def remove_file(response):
    #     try:
    #         os.remove(zip_io)  # Clean up server memory by removing the temporary file
    #     except Exception as error:
    #         app.logger.error("Error removing or closing downloaded zip file handle", error)
    #     return response

    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='converted_images.zip')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'gif', 'png', 'bmp'}

if __name__ == '__main__':
    app.run()
