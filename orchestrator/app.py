#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
import os
from orchestrator import Orchestrator  # Use local import

app = Flask(__name__)
orchestrator = Orchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_request = data.get('request')
    input_text = data.get('text')

    if not user_request or not input_text:
        return jsonify({"error": "Request and input text are required"}), 400

    try:
        result = orchestrator.process_request(user_request, input_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the templates directory exists
    os.makedirs('templates', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)