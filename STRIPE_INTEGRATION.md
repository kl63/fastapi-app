# Stripe Payment Integration

This document explains how to use the Stripe payment integration in your FastAPI e-commerce application.

## Setup

### 1. Get Stripe API Keys

1. Sign up for a Stripe account at [https://stripe.com](https://stripe.com)
2. Go to your Stripe Dashboard: [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)
3. Copy your **Publishable key** and **Secret key** (use test keys for development)

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_51...  # Your Stripe publishable key
STRIPE_SECRET_KEY=sk_test_51...       # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...       # Your Stripe webhook secret (optional for development)
```

### 3. Install Dependencies

The Stripe Python SDK is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## API Endpoints

### Payment Intent Endpoints

#### Create Payment Intent
```http
POST /api/v1/orders/create-payment-intent
```

Create a payment intent for processing payments.

**Request Body:**
```json
{
  "amount": 29.99,
  "currency": "usd",
  "payment_method_id": "pm_1234567890",  // optional
  "customer_id": "cus_1234567890",       // optional
  "metadata": {
    "order_id": "order_123"
  }
}
```

**Response:**
```json
{
  "id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "status": "requires_payment_method",
  "amount": 2999,
  "currency": "usd",
  "metadata": {
    "order_id": "order_123",
    "user_id": "user_456",
    "user_email": "user@example.com"
  }
}
```

#### Create Order with Payment
```http
POST /api/v1/orders/create-order-with-payment
```

Create an order and associated payment intent in one step.

**Request Body:**
```json
{
  "shipping_address_id": "addr_123",
  "billing_address_id": "addr_456",
  "notes": "Please handle with care",
  "payment_method_id": "pm_1234567890",  // optional
  "save_payment_method": false
}
```

**Response:**
```json
{
  "order_id": "order_789",
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "amount": 29.99,
  "status": "requires_payment_method"
}
```

#### Confirm Payment
```http
POST /api/v1/orders/confirm-payment/{order_id}?payment_intent_id=pi_123
```

Confirm payment for an order and update order status.

**Response:**
```json
{
  "message": "Payment confirmed successfully",
  "order_id": "order_789",
  "payment_status": "succeeded"
}
```

### Admin Endpoints

#### Process Refund
```http
POST /api/v1/orders/refund/{order_id}
```

Process a refund for an order (admin only).

**Request Body:**
```json
{
  "payment_intent_id": "pi_1234567890",
  "refund_amount": 15.00  // optional, defaults to full amount
}
```

**Response:**
```json
{
  "message": "Refund processed successfully",
  "refund_id": "re_1234567890",
  "amount": 15.00,
  "status": "succeeded"
}
```

### Webhook Endpoint

#### Stripe Webhook
```http
POST /api/v1/webhooks/stripe
```

Handles Stripe webhook events automatically. Configure this URL in your Stripe Dashboard:
```
https://yourdomain.com/api/v1/webhooks/stripe
```

**Supported Events:**
- `payment_intent.succeeded` - Updates order status to "confirmed"
- `payment_intent.payment_failed` - Updates order status to "cancelled"
- `payment_intent.canceled` - Updates order status to "cancelled"
- `charge.dispute.created` - Logs chargeback for admin review

## Frontend Integration

### Basic Payment Flow

1. **Create Order with Payment Intent:**
   ```javascript
   const response = await fetch('/api/v1/orders/create-order-with-payment', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': 'Bearer ' + token
     },
     body: JSON.stringify({
       shipping_address_id: 'addr_123',
       billing_address_id: 'addr_456'
     })
   });
   
   const { client_secret, order_id } = await response.json();
   ```

2. **Process Payment with Stripe.js:**
   ```javascript
   const stripe = Stripe('pk_test_...');  // Your publishable key
   
   const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
     payment_method: {
       card: cardElement,
       billing_details: {
         name: 'Customer Name',
         email: 'customer@example.com'
       }
     }
   });
   
   if (error) {
     console.error('Payment failed:', error);
   } else if (paymentIntent.status === 'succeeded') {
     console.log('Payment succeeded!');
     // Redirect to success page
   }
   ```

3. **Confirm Payment (Optional):**
   ```javascript
   // This is handled automatically by webhooks, but you can also call manually
   await fetch(`/api/v1/orders/confirm-payment/${order_id}?payment_intent_id=${paymentIntent.id}`, {
     method: 'POST',
     headers: {
       'Authorization': 'Bearer ' + token
     }
   });
   ```

## Testing

### Test Cards

Use these test card numbers in development:

- **Successful payment:** `4242424242424242`
- **Payment requires authentication:** `4000002500003155`
- **Payment is declined:** `4000000000000002`

### Test Webhooks

1. Install Stripe CLI: [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)
2. Login: `stripe login`
3. Forward events to your local server:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
   ```

## Security Best Practices

1. **Never expose secret keys** in frontend code
2. **Use HTTPS** in production
3. **Validate webhook signatures** (already implemented)
4. **Store sensitive data securely** (payment methods are tokenized)
5. **Implement proper error handling** for failed payments
6. **Log payment events** for audit trails

## Error Handling

The integration includes comprehensive error handling:

- **Invalid API keys** - Returns 400 with Stripe error message
- **Insufficient funds** - Handled by Stripe, webhook updates order status
- **Network errors** - Automatic retries by Stripe
- **Webhook failures** - Events are retried by Stripe

## Production Deployment

1. Replace test API keys with live keys in production environment
2. Configure webhook endpoint in Stripe Dashboard
3. Set up monitoring for payment failures
4. Implement proper logging and alerting
5. Test the complete payment flow before going live

## Support

For Stripe-specific issues, refer to:
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Support](https://support.stripe.com/)

For integration issues, check the application logs and ensure all environment variables are properly configured.
