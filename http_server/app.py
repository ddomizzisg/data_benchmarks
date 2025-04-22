from flask import Flask, request, send_from_directory, abort
import os

app = Flask(__name__)
UPLOAD_DIR = '/app/data'

@app.route('/<filename>', methods=['PUT'])
def upload_file(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, 'wb') as f:
        f.write(request.get_data())
    return 'File uploaded', 201

@app.route('/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=8080)
