from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

# Simulate API endpoint
BASE_URL = "http://localhost:5000"

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/create_payment', methods=['POST'])
def create_payment():
    data = request.json
    response = requests.post(f"{BASE_URL}/create_payment", json=data)
    return jsonify(response.json())

@app.route('/check_payment_status/<payment_id>', methods=['GET'])
def check_payment_status(payment_id):
    response = requests.get(f"{BASE_URL}/check_payment_status/{payment_id}")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
