# SynLINK - Razorpay Integration Solution

SynLINK is a versatile payment integration solution that provides both API and website-based methods to integrate Razorpay payments into your applications.

## Features

- API-based integration with unique API keys for multiple applications
- Website-based integration with simple credential management
- Secure payment processing
- Payment verification
- Real-time order creation
- Support for INR currency

## Base URL
```
https://synlink.onrender.com
```

## API Integration Guide

### 1. Initialize Integration

Initialize a new integration and get a payment URL.

```bash
curl -X POST https://synlink.onrender.com/integrate-razorpay \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_RAZORPAY_KEY_ID",
    "secret_key": "YOUR_RAZORPAY_KEY_SECRET",
    "amount": "1000",
    "phone": "9999999999"
  }'
```

**Response:**
```json
{
  "status": "success",
  "payment_url": "https://synlink.onrender.com/payment/YOUR_RAZORPAY_KEY_ID"
}
```

### 2. Create Order (API)

Create a new order using your API key.

```bash
curl -X POST https://synlink.onrender.com/create_order/YOUR_RAZORPAY_KEY_ID \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "id": "order_xxx",
  "amount": 100000,
  "currency": "INR",
  "receipt": "receipt_YOUR_RAZORPAY_KEY_ID"
}
```

### 3. Verify Payment (API)

Verify a payment after completion.

```bash
curl -X POST https://synlink.onrender.com/verify_payment/YOUR_RAZORPAY_KEY_ID \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_xxx",
    "razorpay_order_id": "order_xxx",
    "razorpay_signature": "xxx"
  }'
```

## Website Integration Guide

### 1. Set Credentials

Set your Razorpay credentials for website usage.

```bash
curl -X POST https://synlink.onrender.com/set_credentials \
  -H "Content-Type: application/json" \
  -d '{
    "key_id": "YOUR_RAZORPAY_KEY_ID",
    "key_secret": "YOUR_RAZORPAY_KEY_SECRET"
  }'
```

### 2. Create Order (Website)

Create a new order for your website.

```bash
curl -X POST https://synlink.onrender.com/create_order \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1000",
    "email": "customer@example.com",
    "contact": "9999999999"
  }'
```

### 3. Verify Payment (Website)

Verify a payment for your website.

```bash
curl -X POST https://synlink.onrender.com/verify_payment \
  -H "Content-Type: application/json" \
  -d '{
    "razorpay_payment_id": "pay_xxx",
    "razorpay_order_id": "order_xxx",
    "razorpay_signature": "xxx"
  }'
```

## Response Codes

- 200: Successful operation
- 400: Bad request (missing or invalid parameters)
- 401: Unauthorized (invalid credentials)
- 500: Server error

## Security Notes

1. Always keep your API keys and secret keys secure
2. Never expose your secret key in client-side code
3. Always verify payments server-side
4. Use HTTPS for all API calls

## Implementation Notes

- All amounts should be provided in INR
- Phone numbers should be provided without country code
- API credentials are stored temporarily in memory
- Website credentials persist until the server restarts

## Error Handling

All endpoints return JSON responses with error details:

```json
{
  "status": "error",
  "message": "Error description"
}
```

## Requirements

- Razorpay account with API credentials
- HTTPS enabled endpoint for payment verification
- Valid email for payment notifications
- Support for JSON requests/responses

## Development Setup

1. Clone the repository
2. Install requirements:
```bash
pip install flask razorpay
```
3. Run the application:
```bash
python app.py
```

## Production Considerations

1. Use environment variables for credentials
2. Implement proper session management
3. Add rate limiting
4. Set up monitoring and logging
5. Use a production-grade server instead of Flask's development server

## Support

For support and feature requests, please open an issue in the repository or contact our support team.
