from flask import Flask, jsonify, render_template, request, url_for
import razorpay
import os
from functools import wraps

app = Flask(__name__)

# Store credentials for both API and website usage
credentials_store = {}
website_credentials = {
    'key_id': None,
    'key_secret': None
}

def require_api_credentials(api_key):
    if api_key not in credentials_store:
        return False
    return True

def require_website_credentials(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not website_credentials['key_id'] or not website_credentials['key_secret']:
            return jsonify({'error': 'Website API credentials not set'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

# API Routes
@app.route('/integrate-razorpay', methods=['POST'])
def integrate_razorpay():
    try:
        data = request.json
        api_key = data.get('api_key')
        secret_key = data.get('secret_key')
        amount = data.get('amount')
        phone = data.get('phone')
        
        if not all([api_key, secret_key, amount, phone]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Store credentials
        credentials_store[api_key] = {
            'key_id': api_key,
            'key_secret': secret_key,
            'amount': amount,
            'phone': phone
        }
        
        # Test the credentials
        client = razorpay.Client(auth=(api_key, secret_key))
        test_order = client.order.create({
            'amount': 100,
            'currency': 'INR',
            'receipt': 'test_receipt',
            'payment_capture': 0
        })
        
        # Generate payment URL
        payment_url = url_for('show_payment', api_key=api_key, _external=True)
        return jsonify({'status': 'success', 'payment_url': payment_url})
    
    except Exception as e:
        if api_key in credentials_store:
            del credentials_store[api_key]
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/payment/<api_key>')
def show_payment(api_key):
    if not require_api_credentials(api_key):
        return "Invalid API Key", 400
        
    creds = credentials_store[api_key]
    return render_template('integration.html', 
                         api_key=api_key,
                         amount=creds['amount'],
                         phone=creds['phone'])

@app.route('/create_order/<api_key>', methods=['POST'])
def create_order_api(api_key):
    if not require_api_credentials(api_key):
        return jsonify({'error': 'Invalid API Key'}), 400
        
    try:
        creds = credentials_store[api_key]
        amount = int(float(creds['amount']) * 100)  # Convert to paise
        
        razorpay_client = razorpay.Client(
            auth=(creds['key_id'], creds['key_secret'])
        )
        
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'receipt_{api_key}',
            'notes': {
                'email': 'customer@example.com',
                'contact': creds['phone']
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        return jsonify(order)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/verify_payment/<api_key>', methods=['POST'])
def verify_payment_api(api_key):
    if not require_api_credentials(api_key):
        return jsonify({'error': 'Invalid API Key'}), 400
        
    try:
        creds = credentials_store[api_key]
        payment_data = request.json
        razorpay_client = razorpay.Client(
            auth=(creds['key_id'], creds['key_secret'])
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

# Website Routes
@app.route('/set_credentials', methods=['POST'])
def set_credentials():
    try:
        data = request.json
        website_credentials['key_id'] = data['key_id']
        website_credentials['key_secret'] = data['key_secret']
        
        # Test the credentials
        client = razorpay.Client(
            auth=(website_credentials['key_id'], website_credentials['key_secret'])
        )
        test_order = client.order.create({
            'amount': 100,
            'currency': 'INR',
            'receipt': 'test_receipt',
            'payment_capture': 0
        })
        
        return jsonify({'status': 'success', 'message': 'Credentials verified and stored'})
    except Exception as e:
        website_credentials['key_id'] = None
        website_credentials['key_secret'] = None
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/create_order', methods=['POST'])
@require_website_credentials
def create_order_website():
    try:
        data = request.json
        amount = int(float(data['amount']) * 100)  # Convert to paise
        
        razorpay_client = razorpay.Client(
            auth=(website_credentials['key_id'], website_credentials['key_secret'])
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
@require_website_credentials
def verify_payment_website():
    try:
        payment_data = request.json
        razorpay_client = razorpay.Client(
            auth=(website_credentials['key_id'], website_credentials['key_secret'])
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
