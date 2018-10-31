# File storage with http access

## Requirements


Application requires **Flask and Gunicorn**.

Install requirements for application:

    $ pip install -r requirements.txt

## Usage (start server)


Basic usage (run as daemon):

    $ gunicorn -c gunicorn_settings.py app:app

Test server:

    $ python app.py


# HTTP Verbs


| HTTP METHOD | POST        | GET       	| DELETE      |
| ----------- | ----------- | ------------- | ----------- |
| CRUD OP     | CREATE      | READ      	| DELETE      |
| /           | Upload file | - 			| - 	 	  |
| /hash_code  | -	        | Download file | Delete file |


## Examples

Download file by hash:

	$ curl -X GET 127.0.0.1:8000/abcdefg123

    Hello World! (file content)


Delete file by hash:

	$ curl -X DELETE 127.0.0.1:8000/abcdefg123

    {
    	"info": "File has been deleted.",
    	"status": "200 OK"
	}

Upload file by hash:

    $ curl -F 'file=@path/to/local/file' 127.0.0.1:8000

    {
      "hash": "abcdefg123",
      "info": "File uploaded successfully.",
      "status": "201 Created"
    }


## Tests

The basic way to run tests:

    $ pip install -r requirements.txt
    $ python test_app.py
