from flask import Flask, jsonify, request
import os
from openai import OpenAI

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
print(api_key)

# Initialize the OpenAI client with the API key
client = OpenAI()

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
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # You might want to add a file check here for security (file type, size)
        
        # Perform the transcription using OpenAI's Whisper model
        try:
            # Use the file stream directly rather than saving and reopening
            file_bytes = file.read()

            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=(file.filename, file_bytes, file.content_type)
            )
            return jsonify({'transcription': transcription.text}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')