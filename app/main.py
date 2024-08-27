
from flask import Flask, request, jsonify, session
from gpt import GPT
import os
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = os.urandom(24)  # Set a secret key for the session

# Load environment variables
load_dotenv()

# Initialize GPT instance
gpt_instance = GPT(os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return "Welcome to the GPT Flask App!"

@app.route('/updatefiles', methods=['GET'])
def update_files():
    gpt_instance.update_files()
    return "Files update started successfully"

@app.route('/refreshcache', methods=['GET'])
def update_resumecache():
    gpt_instance.refresh_summary()
    return "Resume cache refreshed successfully"

@app.route('/api/chat', methods=['POST'])
def start_program():
    """
    User interface for starting the program.
    """
    message = request.json.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Load resumeCache.txt data
    with open('resumeCache.txt') as f:
        data = f.readlines()

    # Retrieve conversation history from session
    conversation_history = session.get('conversation_history', [])
    
    # Get the response from GPT
    conversation_history_update = gpt_instance.start_request(message, data, conversation_history)
    
    # Update the session conversation history
    session['conversation_history'] = conversation_history_update
    print(f'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA {conversation_history_update}')
    return jsonify({"conversation_history": conversation_history_update}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)