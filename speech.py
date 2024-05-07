from flask import jsonify
from pathlib import Path
import os
import time

def speech_to_text(file, client):
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
            return transcription.text
        except Exception as e:
            return None

def text_to_speech(text, client):
    # Get the current time in seconds since the epoch
    current_time_seconds = time.time()
    full_path = os.path.join('speech', f"{current_time_seconds}.mp3")
    speech = client.audio.speech.create(
        model="tts-1", 
        voice="alloy",
        input=text
    )
    speech.stream_to_file(full_path)
    return os.getenv('BASE_URL', 'http://127.0.0.1:5000') + "/speech/" + f"{current_time_seconds}.mp3"



