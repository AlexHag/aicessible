from flask import Flask, jsonify, request
import os
from openai import OpenAI
from pymongo import MongoClient
from speech import speech_to_text, text_to_speech
from aicessible_api import chat
import logging

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

@app.route('/audio-chat/<session_id>', methods=['POST'])
def transcribe_audio(session_id):
    try:
        # Check if the post request has the file part
        if 'audiofile' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['audiofile']
        print(file)

        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        user_input = speech_to_text(file, client)
        print(user_input)
        response = chat(session_id, user_input, collection, client)
        speech = text_to_speech(response["response"], client)
        return jsonify({'response_url': speech, 'status': response["status"]}), 200
    except Exception as e:
        print(e)
        error_audio_path = os.getenv('BASE_URL', 'http://127.0.0.1:5000') + "/speech/" + "try_again.mp3"
        return jsonify({'response_url': error_audio_path, 'status': "Failed"}), 500

@app.route('/chat/<session_id>', methods=['POST'])
def chat_text(session_id):
    try:
        data = request.get_json()
        user_input = data["user_input"]
        response = chat(session_id, user_input, collection, client)
        return jsonify({'response': response["response"], 'status': response["status"]}), 200
    
    except Exception as e:
        print(e)
        error_audio_path = os.getenv('BASE_URL', 'http://127.0.0.1:5000') + "/speech/" + "try_again.mp3"
        return jsonify({'response_url': error_audio_path, 'status': "Failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')