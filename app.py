# app.py
from flask import Flask, render_template, request, jsonify
from wine_agent import chat_with_agent
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'response': 'Please send a valid JSON message'})
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'response': 'Please enter a message'})
        
        # Get response from agent
        response = chat_with_agent(message)
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({'response': 'I encountered an error. Please try again.'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Wine Assistant API'})

if __name__ == '__main__':
    print("Starting Wine Assistant Server...")
    print("Visit http://localhost:5000 to chat with the assistant")
    app.run(debug=True, host='0.0.0.0', port=5000)