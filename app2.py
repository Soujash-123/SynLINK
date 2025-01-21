# app.py
from flask import Flask, jsonify, render_template, request
import razorpay
import os
from functools import wraps

app = Flask(__name__)

# Store credentials temporarily in memory
credentials = {
    'key_id': None,
    'key_secret': None
}

def require_credentials(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not credentials['key_id'] or not credentials['key_secret']:
            return jsonify({'error': 'API credentials not set'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_credentials', methods=['POST'])
def set_credentials():
    try:
        data = request.json
        credentials['key_id'] = data['key_id']
        credentials['key_secret'] = data['key_secret']
        
        # Test the credentials by creating a small test order
        client = razorpay.Client(auth=(credentials['key_id'], credentials['key_secret']))
        test_order = client.order.create({
            'amount': 100,  # Minimum amount (₹1)
            'currency': 'INR',
            'receipt': 'test_receipt',
            'payment_capture': 0  # Don't auto capture the payment
        })
        
        return jsonify({'status': 'success', 'message': 'Credentials verified and stored'})
    except Exception as e:
        credentials['key_id'] = None
        credentials['key_secret'] = None
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/create_order', methods=['POST'])
@require_credentials
def create_order():
    try:
        data = request.json
        amount = int(float(data['amount']) * 100)  # Convert to paise
        
        razorpay_client = razorpay.Client(
            auth=(credentials['key_id'], credentials['key_secret'])
        )
        
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': 'order_receipt_11',
            'notes': {
                'email': data.get('email', 'customer@example.com'),
                'contact': data.get('contact', '')
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/verify_payment', methods=['POST'])
@require_credentials
def verify_payment():
    try:
        payment_data = request.json
        razorpay_client = razorpay.Client(
            auth=(credentials['key_id'], credentials['key_secret'])
        )
        
        params_dict = {
            'razorpay_payment_id': payment_data['razorpay_payment_id'],
            'razorpay_order_id': payment_data['razorpay_order_id'],
            'razorpay_signature': payment_data['razorpay_signature']
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        return jsonify({'status': 'success', 'message': 'Payment verified successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

