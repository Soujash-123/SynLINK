# Razorpay Payment Link Integration with Flask

This Flask application integrates Razorpay's Payment Link API to create, track, and verify payment links. It supports redirect-based callbacks and optional redirection to a custom URL after payment completion.

## Live Demo
Hosted at: [https://synlink-1.onrender.com](https://synlink-1.onrender.com)

---

## Features
- Create Razorpay payment links via API
- Check payment status by payment ID
- Web-based UI for payment tracking
- Razorpay webhook integration for real-time updates
- Auto-expiry of payment links after 30 minutes
- Optional redirect after payment completion
- CORS enabled for cross-origin requests

---

## API Endpoints

### `GET /`
Renders the homepage (`index.html`).

### `POST /create_payment`
Creates a Razorpay payment link.

#### Request Body (JSON):
```json
{
  "amount": "500",
  "phone": "9876543210",
  "razorpay_key_id": "YOUR_KEY_ID",
  "razorpay_key_secret": "YOUR_SECRET_KEY",
  "redirect_url": "https://yourdomain.com/after-payment"  // Optional
}
```

#### Response:
```json
{
  "payment_id": "<UUID>",
  "payment_url": "https://rzp.io/l/xyz",
  "razorpay_payment_id": "plink_LWxyzabc123",
  "status": "created"
}
```

#### Example CURL Command:
```bash
curl -X POST https://synlink-1.onrender.com/create_payment \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "500",
    "phone": "9876543210",
    "razorpay_key_id": "YOUR_KEY_ID",
    "razorpay_key_secret": "YOUR_SECRET_KEY",
    "redirect_url": "https://yourdomain.com/after-payment"
  }'
```

### `GET /payment/<payment_id>`
Renders the payment status page for the given `payment_id`.

### `GET /check_payment_status/<payment_id>`
Checks and returns the current status of the payment.

#### Response:
```json
{
  "payment_id": "<UUID>",
  "razorpay_id": "plink_LWxyzabc123",
  "status": "paid",
  "amount": "500",
  "phone": "9876543210"
}
```

#### Example CURL Command:
```bash
curl https://synlink-1.onrender.com/check_payment_status/<payment_id>
```

### `GET /payment_callback/<payment_id>`
Redirect/callback URL after Razorpay payment. Renders either `success.html` or `failure.html` depending on the final status.

### `POST /webhook`
Razorpay webhook endpoint for updating payment status in real-time.

#### Example CURL Command:
```bash
curl -X POST https://synlink-1.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "payment_link": {
        "entity": {
          "id": "plink_LWxyzabc123",
          "status": "paid"
        }
      }
    }
  }'
```

---

## Razorpay Webhook Configuration
To receive webhook updates:
- Set the endpoint to: `https://synlink-1.onrender.com/webhook`
- Select events like `payment_link.paid`, `payment_link.expired`, etc.

---

## Setup Instructions
1. Clone this repository.
2. Install dependencies:
```bash
pip install flask razorpay flask-cors
```
3. Run the app:
```bash
python app.py
```
4. Make requests to `http://localhost:5001` or deploy to a platform like Render.

---

## Notes
- The payment records are stored in memory (`payment_records` dictionary). For production, replace with a database.
- Razorpay key ID and secret are passed in the request for flexibility, but it's recommended to secure these via environment variables or backend storage.

---

## License
MIT License

