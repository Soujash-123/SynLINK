from flask import Flask, request, jsonify, render_template, url_for, redirect
import razorpay
import json
import os
import uuid
from datetime import datetime, timedelta
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
uri = "mongodb+srv://oppurtunest:hAPV3Tf0QoB0GgiQ@cluster0.mbbgm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.synlink_payments
transactions_collection = db.transactions
invoices_collection = db.invoices

# Dictionary to store payment information (keeping for backwards compatibility)
payment_records = {}

# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/<payment_id>')
def display_payment(payment_id):
    # Check if payment ID exists
    if payment_id not in payment_records:
        return render_template('error.html', message='Invalid payment ID')
    
    payment_info = payment_records[payment_id]
    
    return render_template('display_payment.html', 
                         payment_url=payment_info.get('payment_url', '#'))

@app.route('/create_payment', methods=['POST'])
def create_payment():
    try:
        # Extract parameters from request
        data = request.json
        amount = data.get('amount')
        phone = data.get('phone')
        razorpay_key_id = data.get('razorpay_key_id')
        razorpay_key_secret = data.get('razorpay_key_secret')
        redirect_url = data.get('redirect_url', '#')
        
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
        payment_url = payment_link['short_url']
        
        # Create transaction document
        transaction_data = {
            'payment_id': payment_id,
            'razorpay_id': payment_link['id'],
            'amount': amount,
            'phone': phone,
            'status': 'created',
            'created_at': datetime.now(),
            'razorpay_key_id': razorpay_key_id,
            'razorpay_key_secret': razorpay_key_secret,
            'redirect_url': redirect_url,
            'payment_url': payment_url,
            'expire_by': datetime.fromtimestamp(expire_by),
            'payment_link_data': payment_link
        }
        
        # Store in MongoDB
        transactions_collection.insert_one(transaction_data)
        
        # Store in memory (keeping for backwards compatibility)
        payment_records[payment_id] = {
            'razorpay_id': payment_link['id'],
            'amount': amount,
            'phone': phone,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'razorpay_key_id': razorpay_key_id,
            'razorpay_key_secret': razorpay_key_secret,
            'redirect_url': redirect_url,
            'payment_url': payment_url
        }
        
        # Only return the display URL for the iframe page
        display_url = url_for('display_payment', payment_id=payment_id, _external=True)
        return jsonify({
            'payment_id': payment_id,
            'display_url': display_url,
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
                          razorpay_id=payment_info['razorpay_id'],
                          redirect_url=payment_info.get('redirect_url', '#'))

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
    # Check payment in MongoDB
    transaction = transactions_collection.find_one({'payment_id': payment_id})
    
    if transaction:
        # Initialize Razorpay client
        client = razorpay.Client(auth=(
            transaction['razorpay_key_id'],
            transaction['razorpay_key_secret']
        ))
        
        try:
            # Fetch the current status from Razorpay
            razorpay_payment = client.payment_link.fetch(transaction['razorpay_id'])
            new_status = razorpay_payment['status']
            
            # Update MongoDB
            transactions_collection.update_one(
                {'payment_id': payment_id},
                {
                    '$set': {
                        'status': new_status,
                        'updated_at': datetime.now(),
                        'payment_details': razorpay_payment
                    }
                }
            )
            
            # If paid, fetch and store invoice
            if new_status == 'paid':
                try:
                    invoice = client.invoice.fetch(razorpay_payment['invoice_id'])
                    invoices_collection.insert_one({
                        'payment_id': payment_id,
                        'razorpay_id': transaction['razorpay_id'],
                        'invoice_id': razorpay_payment['invoice_id'],
                        'invoice_data': invoice,
                        'created_at': datetime.now()
                    })
                except Exception as e:
                    print(f"Error fetching invoice: {str(e)}")
            
            # Update in-memory store (for backwards compatibility)
            if payment_id in payment_records:
                payment_records[payment_id]['status'] = new_status
        
        except Exception as e:
            print(f"Error in payment callback: {str(e)}")
    
    # Redirect based on status
    if transaction and transaction.get('status') == 'paid':
        return render_template('success.html', 
                             payment_id=payment_id,
                             redirect_url=transaction.get('redirect_url', '#'))
    else:
        return render_template('failure.html', payment_id=payment_id)

@app.route('/webhook', methods=['POST'])
def razorpay_webhook():
    try:
        webhook_data = request.json
        
        if 'payload' in webhook_data and 'payment_link' in webhook_data['payload']:
            razorpay_id = webhook_data['payload']['payment_link']['entity']['id']
            new_status = webhook_data['payload']['payment_link']['entity']['status']
            
            # Update MongoDB
            transaction = transactions_collection.find_one({'razorpay_id': razorpay_id})
            if transaction:
                # Initialize Razorpay client
                client = razorpay.Client(auth=(
                    transaction['razorpay_key_id'],
                    transaction['razorpay_key_secret']
                ))
                
                # Update transaction status
                transactions_collection.update_one(
                    {'razorpay_id': razorpay_id},
                    {
                        '$set': {
                            'status': new_status,
                            'updated_at': datetime.now(),
                            'webhook_data': webhook_data
                        }
                    }
                )
                
                # If paid, fetch and store invoice
                if new_status == 'paid':
                    try:
                        payment_details = client.payment_link.fetch(razorpay_id)
                        if 'invoice_id' in payment_details:
                            invoice = client.invoice.fetch(payment_details['invoice_id'])
                            invoices_collection.insert_one({
                                'payment_id': transaction['payment_id'],
                                'razorpay_id': razorpay_id,
                                'invoice_id': payment_details['invoice_id'],
                                'invoice_data': invoice,
                                'created_at': datetime.now()
                            })
                    except Exception as e:
                        print(f"Error fetching invoice in webhook: {str(e)}")
                
                # Update in-memory store (for backwards compatibility)
                payment_id = transaction['payment_id']
                if payment_id in payment_records:
                    payment_records[payment_id]['status'] = new_status
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/invoice/<payment_id>')
def get_invoice_url(payment_id):
    # Get transaction data from MongoDB
    transaction = transactions_collection.find_one({'payment_id': payment_id})
    if not transaction:
        return jsonify({'error': 'Invalid payment ID'}), 404
    
    # Create the invoice URL
    invoice_url = url_for('display_invoice_iframe', payment_id=payment_id, _external=True)
    return jsonify({
        'invoice_url': invoice_url
    })

@app.route('/inv/<payment_id>')
def display_invoice_iframe(payment_id):
    # Get transaction data from MongoDB
    transaction = transactions_collection.find_one({'payment_id': payment_id})
    if not transaction:
        return render_template('error.html', message='Invalid payment ID')
    
    return render_template('invoice.html',
                         payment_url=transaction.get('payment_url'),
                         payment_id=payment_id)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="5001")
