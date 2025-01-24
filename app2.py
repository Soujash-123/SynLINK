# app.py
from flask import Flask, jsonify, request, render_template
import stripe

app = Flask(__name__)

# Test keys - replace with your actual test keys from Stripe dashboard
stripe.api_key = 'sk_test_your_secret_key'
publishable_key = 'pk_test_your_publishable_key'

@app.route('/')
def index():
    return render_template('index.html', publishable_key=publishable_key)

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = request.json
        amount = data.get('amount', 1000)  # Amount in cents, e.g., 1000 = $10.00

        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent.client_secret
        })

    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == '__main__':
    app.run(debug=True)
