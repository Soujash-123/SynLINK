from flask import Flask, request, jsonify, render_template, url_for, redirect
import razorpay
import json
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# Dictionary to store payment information
payment_records = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_payment', methods=['POST'])
def create_payment():
    try:
        # Extract parameters from request
        data = request.json
        amount = data.get('amount')
        phone = data.get('phone')
        razorpay_key_id = data.get('razorpay_key_id')
        razorpay_key_secret = data.get('razorpay_key_secret')
        
        # Validate inputs
        if not all([amount, phone, razorpay_key_id, razorpay_key_secret]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        # Generate unique payment ID
        payment_id = str(uuid.uuid4())
        
        # Set payment expiry time (30 minutes from now)
        expire_by = int((datetime.now() + timedelta(minutes=30)).timestamp())
        
        # Create payment link
        payment_data = {
            'amount': int(float(amount) * 100),  # Convert to paise
            'currency': 'INR',
            'accept_partial': False,
            'expire_by': expire_by,
            'reference_id': payment_id,
            'description': 'Payment for order',
            'customer': {
                'contact': phone
            },
            'notify': {
                'sms': True,
                'email': False
            },
            'reminder_enable': True,
            'notes': {
                'phone': phone
            },
            'callback_url': url_for('payment_callback', payment_id=payment_id, _external=True),
            'callback_method': 'get'
        }
        
        # Create Razorpay payment link
        payment_link = client.payment_link.create(payment_data)
        
        # Store payment info
        payment_records[payment_id] = {
            'razorpay_id': payment_link['id'],
            'amount': amount,
            'phone': phone,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'razorpay_key_id': razorpay_key_id,
            'razorpay_key_secret': razorpay_key_secret
        }
        
        # Return payment URL and ID
        return jsonify({
            'payment_id': payment_id,
            'payment_url': payment_link['short_url'],
            'razorpay_payment_id': payment_link['id'],
            'status': 'created'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment/<payment_id>', methods=['GET'])
def payment_page(payment_id):
    # Check if payment ID exists
    if payment_id not in payment_records:
        return render_template('error.html', message='Invalid payment ID')
    
    payment_info = payment_records[payment_id]
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(
        payment_info['razorpay_key_id'],
        payment_info['razorpay_key_secret']
    ))
    
    # Fetch the current status from Razorpay
    try:
        razorpay_payment = client.payment_link.fetch(payment_info['razorpay_id'])
        payment_info['status'] = razorpay_payment['status']
        payment_records[payment_id] = payment_info
    except:
        # If there's an error fetching, use the stored status
        pass
    
    return render_template('payment.html', 
                          payment_id=payment_id, 
                          amount=payment_info['amount'],
                          razorpay_key_id=payment_info['razorpay_key_id'],
                          razorpay_id=payment_info['razorpay_id'])

@app.route('/check_payment_status/<payment_id>', methods=['GET'])
def check_payment_status(payment_id):
    # Check if payment ID exists
    if payment_id not in payment_records:
        return jsonify({'error': 'Invalid payment ID'}), 404
    
    payment_info = payment_records[payment_id]
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(
        payment_info['razorpay_key_id'],
        payment_info['razorpay_key_secret']
    ))
    
    # Fetch the current status from Razorpay
    try:
        razorpay_payment = client.payment_link.fetch(payment_info['razorpay_id'])
        payment_info['status'] = razorpay_payment['status']
        payment_records[payment_id] = payment_info
        
        return jsonify({
            'payment_id': payment_id,
            'razorpay_id': payment_info['razorpay_id'],
            'status': payment_info['status'],
            'amount': payment_info['amount'],
            'phone': payment_info['phone']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment_callback/<payment_id>', methods=['GET'])
def payment_callback(payment_id):
    # Update payment status
    if payment_id in payment_records:
        payment_info = payment_records[payment_id]
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(
            payment_info['razorpay_key_id'],
            payment_info['razorpay_key_secret']
        ))
        
        # Fetch the current status from Razorpay
        try:
            razorpay_payment = client.payment_link.fetch(payment_info['razorpay_id'])
            payment_info['status'] = razorpay_payment['status']
            payment_records[payment_id] = payment_info
        except:
            pass
    
    # Redirect to a success/failure page based on payment status
    if payment_id in payment_records and payment_records[payment_id]['status'] == 'paid':
        return render_template('success.html', payment_id=payment_id)
    else:
        return render_template('failure.html', payment_id=payment_id)

@app.route('/webhook', methods=['POST'])
def razorpay_webhook():
    # This endpoint can be configured in Razorpay dashboard for real-time updates
    try:
        webhook_data = request.json
        
        if 'payload' in webhook_data and 'payment_link' in webhook_data['payload']:
            razorpay_id = webhook_data['payload']['payment_link']['entity']['id']
            
            # Find the payment record with this razorpay_id
            for payment_id, payment_info in payment_records.items():
                if payment_info['razorpay_id'] == razorpay_id:
                    payment_info['status'] = webhook_data['payload']['payment_link']['entity']['status']
                    payment_records[payment_id] = payment_info
                    break
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)