import json
from datetime import datetime
import os
from flask import Flask, render_template, request
import uuid
from pymongo import MongoClient
from minio import Minio


minio_client = Minio("172.17.66.179:9000",
    access_key=os.getenv('MINIO_ACCESS_KEY'),
    secret_key=os.getenv('MINIO_SECRET_KEY'),
    secure=False
)

mongo_client = MongoClient("172.17.66.179", username = os.getenv('MONGO_INITDB_ROOT_USERNAME'), password = os.getenv('MONGO_INITDB_ROOT_PASSWORD'), port=27017)
db = mongo_client.flask_db
messages = db.messages
print(messages)

UPLOAD_FOLDER ='./static/images'

app = Flask(__name__)


def read_messages_from_file():
    """ Read all messages from a JSON file"""
    with open('data.json') as messages_file:
        return json.load(messages_file)

def read_mongo():
    found_messages = list(messages.find().sort({"age":1}).limit(10))
    return found_messages

def insert_blob(img_path):
    filename = (img_path).split('/')[-1]
    minio_client.fput_object('images', filename, img_path)
    return filename

def insert_mongo(content, img_path):
    new_message 	= {
        'id': str(uuid.uuid4()),
        'content': content,
        'img_path': img_path,
        'timestamp': datetime.now().isoformat(" ", "seconds")
    }

    try:
        messages.insert_one(new_message)
    except exceptions.CosmosResourceExistsError:
        print("Resource already exists, didn't insert message.")



def append_message_to_file(content, blob_path):
    """ Read the contents of JSON file, add this message to it's contents, then write it back to disk. """
    data = read_messages_from_file()
    new_message = {
        'content': content,
        'img_path': blob_path,
        'timestamp': datetime.now().isoformat(" ", "seconds")
    }

    data['messages'].append(new_message)

    with open('data.json', mode='w') as messages_file:
        json.dump(data, messages_file)



# The Flask route, defining the main behaviour of the webserver:
@app.route("/handle_message", methods=['POST'])
def handleMessage():
    new_message = request.form['msg']

    img_path = ""
    blob_path = ""
    if('file' in request.files and request.files['file']):
        image = request.files['file']
        img_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(img_path)
        filename = insert_blob(img_path) 
	
        blob_path = "http://172.17.66.179:9000/images/"+filename

    if new_message:
        insert_mongo(new_message, blob_path)

    return render_template('handle_message.html', message=new_message)



# The Flask route, defining the main behaviour of the webserver:
@app.route("/", methods=['GET'])
def htmlForm():

    data = read_mongo()

    # Return a Jinja HTML template, passing the messages as an argument to the template:
    return render_template('home.html', messages=data)
