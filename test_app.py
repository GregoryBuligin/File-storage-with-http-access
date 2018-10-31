#!/usr/bin/env python3
import unittest
import os
import io
import hashlib
import json
import shutil

from app import app


TEST_STORE_PATH = 'test_store'


class AppTestCase(unittest.TestCase):
    """Testing file storage HTTP API"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = app
        self.app.config['UPLOAD_FOLDER'] = TEST_STORE_PATH
        self.client = self.app.test_client

        if not os.path.exists(self.app.config['UPLOAD_FOLDER']):
            os.mkdir(self.app.config['UPLOAD_FOLDER'])


    def tearDown(self):
        """Teardown all initialized variables."""
        shutil.rmtree(app.config['UPLOAD_FOLDER'])


    def test_status_code_405(self):
        """Test API can return correct 405-response."""

        res = self.client().get('/')
        self.assertEqual(res.status_code, 405)
        self.assertIn('405 Method Not Allowed', str(res.data))


    def test_status_code_404(self):
        """Test API can return correct 404-response."""

        res = self.client().get('/incorrect_hash')
        self.assertEqual(res.status_code, 404)
        self.assertIn('404 Not Found', str(res.data))


    def test_status_code_400(self):
        """Test API can return correct 400-response."""
        res = self.client().post('/')
        self.assertEqual(res.status_code, 400)
        self.assertIn('400 Bad Request', str(res.data))


    def test_upload_wrong_file_extension(self):
        """
        Test API can return correct response to upload file with
        wrong file extension.
        """

        res = self.client().post('/', data={
            'file': (io.BytesIO(bytes(b'test')), 'test.error'),
        })

        self.assertEqual(res.status_code, 400)
        self.assertIn('400 Bad Request', str(res.data))
        self.assertIn('Wrong file extension.', str(res.data))


    def test_file_upload(self):
        """
        Test API can return correct response to upload file.
        """
        file_content = bytes(b'test')
        img_key = hashlib.md5(file_content).hexdigest()
        res = self.client().post('/', data={
            'file': (io.BytesIO(file_content), 'test.txt'),
        })

        data = json.loads(str(res.data.decode('utf8').replace("'", '"')))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(img_key, data['hash'])
        self.assertIn('201 Created', str(res.data))
        self.assertIn('File uploaded successfully.', str(res.data))
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                          img_key[0:2],
                                          img_key)

        with open(uploaded_file_path) as f:
            self.assertEqual(file_content.decode("utf-8"), f.read())


    def test_file_already_exists_upload(self):
        """
        Test API can return the correct answer to
        the uploaded file that is uploaded.
        """

        file_content = bytes(b'already exists')
        img_key = hashlib.md5(file_content).hexdigest()
        res = self.client().post('/', data={
            'file': (io.BytesIO(file_content), 'file.txt'),
        })

        data = json.loads(str(res.data.decode('utf8').replace("'", '"')))
        # File creation
        self.assertEqual(res.status_code, 201)
        self.assertEqual(img_key, data['hash'])

        res = self.client().post('/', data={
            'file': (io.BytesIO(file_content), 'file.txt'),
        })

        self.assertEqual(res.status_code, 200)
        self.assertIn('File already exists.', str(res.data))


    def test_file_download(self):
        """Test API can return file to client by hash"""

        # Upload file
        file_content = bytes(b'download test')
        img_key = hashlib.md5(file_content).hexdigest()
        res = self.client().post('/', data={
            'file': (io.BytesIO(file_content), 'download.txt'),
        })
        self.assertEqual(res.status_code, 201)

        # Download file
        current = json.loads(str(res.data.decode('utf8').replace("'", '"')))
        file_hash = current['hash']
        res = self.client().get('/{}'.format(file_hash))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, file_content)
        res.close()


    def test_file_delete(self):
        """Test API can delete by hash"""

        # Upload file
        file_content = bytes(b'delete test')
        img_key = hashlib.md5(file_content).hexdigest()
        res = self.client().post('/', data={
            'file': (io.BytesIO(file_content), 'delete.txt'),
        })
        self.assertEqual(res.status_code, 201)
        current = json.loads(str(res.data.decode('utf8').replace("'", '"')))
        file_hash = current['hash']

        # Delete file
        res = self.client().delete('/{}'.format(file_hash))
        self.assertEqual(res.status_code, 200)
        self.assertIn('File has been deleted.', str(res.data))


    def test_deletion_of_a_non_existent_file(self):
        """Test API can't delete a non-existent file by hash"""

        res = self.client().delete('/non_existent_hash')
        self.assertEqual(res.status_code, 404)
        self.assertIn('404 Not Found', str(res.data))


# Make the tests executable
if __name__ == "__main__":
    unittest.main()
