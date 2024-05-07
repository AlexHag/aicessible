from flask import Flask, jsonify, request
import os
from openai import OpenAI
from pymongo import MongoClient
from speech import speech_to_text, text_to_speech

app = Flask(__name__,  static_folder='speech', static_url_path='/speech')

# Get the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
print(api_key)

# Initialize the OpenAI client with the API key
client = OpenAI()

mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb+srv://bharatnadkarni:OWzhc3LC1KnYjzX6@cluster0.x5gwek4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
print(mongo_client)
db = mongo_client['accessible']

collection = db.actions


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Aiccesible API'})

@app.route('/speech-to-text', methods=['POST'])
def transcribe_audio():
    # Check if the post request has the file part
    if 'audiofile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['audiofile']
    print(file)
    
    # If the user does not select a file, the browser submits an
    # empty file without a filename.

    response = speech_to_text(file, client)
    print(response)
    speech = text_to_speech(response, client)
    return speech
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')