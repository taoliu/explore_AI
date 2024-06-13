from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_session import Session
import uuid
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# In-memory storage for chat sessions
chat_sessions = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/session', methods=['POST'])
def create_session():
    data = request.json
    session_name = data.get('session_name')
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {'name': session_name, 'history': []}
    return jsonify({"session_id": session_id, "session_name": session_name})

@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id in chat_sessions:
        return jsonify({"session_id": session_id, "history": chat_sessions[session_id]['history']})
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({"message": "Session deleted"})
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route('/session/<session_id>', methods=['POST'])
def save_message(session_id):
    if session_id in chat_sessions:
        message = request.json
        chat_sessions[session_id]['history'].append(message)
        return jsonify({"message": "Message saved"})
    else:
        return jsonify({"error": "Session not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
