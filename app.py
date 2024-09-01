#TODO: fix formatting of the index.html output
#TODO: make routine in aws

from flask import Flask, request, jsonify, session, render_template, Blueprint, logging
from gpt import GPT
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, resources={r"/api/*": {"origins": "http://35.183.93.138/"}}, supports_credentials=True)

# Load environment variables
load_dotenv()

# Initialize GPT instance
gpt_instance = GPT(os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def start_program():
    """
    User interface for starting the program.
    """
    print('Starting program...')
    message = request.json.get('message', '')
    session.setdefault('text', [])

    try:
        with open('resumeCache.txt') as f:
            data = f.readlines()
    except FileNotFoundError:
        return jsonify({"error": "resumeCache.txt failed / doesn't exist. Kindly report to techsupport@synfiny.com"}), 400

    # Retrieve conversation history from session
    cookie = session.get('text', [])
    print(f'\n\n\nCONVO HISTORY: {cookie}\n\n\n')

    send = cookie
    # Get the response from GPT
    # Make sure to pass a copy of the conversation history to avoid unintentional mutations
    reply = gpt_instance.start_request(message, data, send)

    print(f'\n\n\nCONVO UPDATE: {reply}\n\n\n')

    # Update the conversation history
    print(f'\n\n\nCONVO: {cookie}\n\n\n')
    
    # Ensure no circular reference in session data
    session['text'] = cookie  # Re-assign session to ensure it's stored properly
    
    # Return a serializable structure
    response = jsonify({"conversation_history": cookie})
    response.status_code = 200
    app.logger.info("Request received: %s", request.json)
    return add_cors_headers(response)

@app.route('/close', methods=['POST'])
def close():
    """
    User closing the program.
    """
    print('Cleaning cookie...')
    try:
        session.pop('text')
        return jsonify({"message": "Session cleared"}), 200
    except KeyError:
        pass
    return jsonify({"message": "No session to clear"}), 200
from flask import request

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Private-Network'] = 'true'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)