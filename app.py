#!/usr/bin/env python3
import os
import hashlib

from flask import Flask, abort, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'store'
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg', 'doc', 'xls', 'mpp',
                          'pdf', 'ppt', 'tiff', 'bmp', 'docx', 'xlsx', 'pptx',
                          'ps', 'odt', 'ods', 'odp', 'odg', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    """Check file extension."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(400)
def bad_request(error):
    """Bad request error handler."""

    return jsonify({
        'status': '400 Bad Request'
    }), 400


@app.errorhandler(404)
def page_not_found(error):
    """Page not found error handler."""

    return jsonify({
        'status': '404 Not Found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Method not allowed error handler."""

    return jsonify({
        'status': '405 Method Not Allowed'
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    """Internal server error handler."""

    return jsonify({
        'status': '500 Internal Server Error'
    }), 500


@app.route('/', methods=['POST'])
def upload_file_handler():
    """File upload handler."""

    file = request.files['file']
    if file and allowed_file(secure_filename(file.filename)):
        img_key = hashlib.md5(file.read()).hexdigest()
        subdir = img_key[0:2]
        dir_name = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
        if os.path.exists(os.path.join(dir_name, img_key)):
            return jsonify({
                'info': 'File already exists.',
                'hash': img_key
            }), 200

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        file.seek(0)
        file.save(os.path.join(dir_name, img_key))
        file.close()

        return jsonify({
            'status': '201 Created',
            'info': 'File uploaded successfully.',
            'hash': img_key
        }), 201

    else:
        return jsonify({
            'status': '400 Bad Request',
            'info': 'Wrong file extension.',
        }), 400


@app.route('/<string:file_hash>', methods=['GET', 'DELETE'])
def storage_handler(file_hash):
    """File download and delete handler."""

    file_hash = secure_filename(file_hash)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                             file_hash[0:2],
                             file_hash)

    file_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_hash[0:2])

    # Download file
    if request.method == 'GET':
        if os.path.exists(file_path):
            return send_from_directory(file_dir,
                                       file_hash,
                                       as_attachment=True), 200

    # Delete file
    elif request.method == 'DELETE':
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                os.rmdir(file_dir)
            except OSError:
                pass
            return jsonify({
                'status': '200 OK',
                'info': 'File has been deleted.',
            }), 200

    abort(404)


# Make the file executable
if __name__ == '__main__':
    # Run test server
    app.run(host='127.0.0.1', debug=True, port=3000)
