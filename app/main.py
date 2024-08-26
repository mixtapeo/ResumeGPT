from flask import Flask, request, jsonify
from gpt import GPT
import os
from dotenv import load_dotenv
import threading
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# Initialize GPT instance
gpt_instance = GPT(os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return "Welcome to the GPT Flask App!"

@app.route('/updatefiles', methods=['GET'])
def update_files():
    def update():
        gpt_instance.update_files()

    thread = threading.Thread(target=update)
    thread.start()
    return jsonify({"message": "Files update started successfully"}), 200

@app.route('/refreshcache', methods=['GET'])
def update_resumecache():
    gpt_instance.refresh_summary()
    return jsonify({"message": "Resume cache refreshed successfully"}), 200

@app.route('/api/chat', methods=['POST'])
def start_program():
    message = request.json.get('message', '')
    if not message:
        return jsonify({"error": "No message provided"}), 400

    with open('resumeCache.txt') as f:
        data = f.readlines()

    conversation_history = []
    conversation_history = gpt_instance.start_request(message, data, conversation_history)

    return jsonify({"conversation_history": conversation_history}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)