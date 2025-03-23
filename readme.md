# Razorpay Payment Gateway API

A Flask-based API for integrating Razorpay payment gateway with support for Google Pay and card payments. This API creates payment links with unique IDs and provides endpoints to check payment status.

## Features

- Generate unique payment URLs with custom payment IDs
- Support for multiple payment methods (Google Pay, cards)
- Real-time payment status tracking
- Automatic window closing after successful payment
- Webhook support for payment status updates
- Simple web interface for testing

## Prerequisites

- Python 3.6+
- Flask
- Razorpay account with API keys

## Installation

1. Clone the repository or download the source code:

```bash
git clone https://github.com/yourusername/razorpay-payment-gateway.git
cd razorpay-payment-gateway
```

2. Install the required packages:

```bash
pip install flask razorpay uuid
```

3. Create the directory structure:

```
/your-project
  /templates
    index.html
    payment.html
    success.html
    failure.html
    error.html
  app.py
```

4. Place the provided files in their respective locations.

## Configuration

No additional configuration files are needed. The API uses the Razorpay credentials provided in the API calls.

## Usage

### Start the server

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### API Endpoints

#### 1. Create Payment Link

```
POST /create_payment
```

Request body:
```json
{
  "razorpay_key_id": "your_key_id",
  "razorpay_key_secret": "your_key_secret",
  "amount": 1000,
  "phone": "9876543210"
}
```
(Avoid using numbers like 9999999999
Response:
```json
{
  "payment_id": "uuid-generated-payment-id",
  "payment_url": "https://rzp.io/i/abcdefgh",
  "razorpay_payment_id": "razorpay-payment-id",
  "status": "created"
}
```

#### 2. Check Payment Status

```
GET /check_payment_status/{payment_id}
```

Response:
```json
{
  "payment_id": "uuid-generated-payment-id",
  "razorpay_id": "razorpay-payment-id",
  "status": "paid",
  "amount": 1000,
  "phone": "9999999999"
}
```

#### 3. Webhook for Real-time Updates

```
POST /webhook
```

Configure this URL in your Razorpay dashboard to receive real-time payment updates.

### Web Interface

A simple web interface is available at the root URL (`/`) for testing the payment flow. You can:

1. Create payment links
2. Check payment status
3. View API documentation

## Payment Flow

1. API receives a request to create a payment with amount and phone number
2. A unique payment ID is generated and a Razorpay payment link is created
3. The payment URL is returned to the client
4. When opened, the payment URL shows the Razorpay payment interface with Google Pay and card payment options
5. After payment completion, the user is redirected to a success or failure page
6. The payment window automatically closes after successful payment
7. The payment status can be checked via the status endpoint

## In-Memory Storage

The application uses an in-memory dictionary to store payment information. In a production environment, you should replace this with a persistent database.

```python
# Replace this:
payment_records = {}

# With a database solution like:
# - SQLite for simple applications
# - PostgreSQL/MySQL for production applications
# - Redis for caching and quick lookup
```

## Security Considerations

1. In a production environment, never expose your Razorpay Secret Key in frontend code
2. Implement proper authentication for your API endpoints
3. Use HTTPS for all communications
4. Validate all incoming data
5. Consider implementing rate limiting to prevent abuse

## Customization

You can customize the payment experience by:

1. Modifying the HTML templates in the `/templates` directory
2. Adjusting the CSS styles
3. Adding additional payment options through the Razorpay dashboard
4. Implementing email notifications after payment completion

## Webhook Integration

For reliable payment status updates, configure webhooks in your Razorpay dashboard:

1. Log in to your Razorpay dashboard
2. Go to Settings > Webhooks
3. Add a new webhook with your server's URL: `https://your-domain.com/webhook`
4. Select the event types to listen for (at minimum, `payment.authorized`)

## Troubleshooting

### Common Issues

1. **Payment creation fails**: Verify your Razorpay API keys
2. **Callback URL not working**: Ensure your server is publicly accessible or use tools like ngrok for testing
3. **Payment status not updating**: Check webhook configuration and server logs

### Debug Mode

The Flask application runs in debug mode by default. For production, set:

```python
if __name__ == '__main__':
    app.run(debug=False)
```

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Razorpay](https://razorpay.com/)
- [Bootstrap](https://getbootstrap.com/)
