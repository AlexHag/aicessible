from flask import Flask, jsonify, request
import os
from openai import OpenAI
from pymongo import MongoClient
from speech import speech_to_text, text_to_speech
from aicessible_api import chat

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

@app.route('/chat/<session_id>', methods=['POST'])
def transcribe_audio(session_id):
    # Check if the post request has the file part
    if 'audiofile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['audiofile']
    print(file)

    # If the user does not select a file, the browser submits an
    # empty file without a filename.

    user_input = speech_to_text(file, client)
    response = chat(session_id, user_input, collection, client)
    speech = text_to_speech(response["response"], client)
    return jsonify({'response_url': speech, 'status': response["status"]}), 200
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')