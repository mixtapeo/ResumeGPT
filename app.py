#TODO: fix formatting of the index.html output
#TODO: make routine in aws

from flask import Flask, request, jsonify, session, render_template, Blueprint
from gpt import GPT
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask.sessions import SecureCookieSessionInterface
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(minutes=5)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
CORS(app, supports_credentials=True)
# Load environment variables
load_dotenv()

# Initialize GPT instance
gpt_instance = GPT(os.getenv('OPENAI_API_KEY'))

site = Blueprint('site', __name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def start_program():
    """
    User interface for starting the program.
    """
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
    return jsonify({"conversation_history": cookie}), 200

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

if __name__ == '__main__':
    app.run(debug=True)