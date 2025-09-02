# Stripe API Integration Guide

This document provides technical details for integrating your frontend application with the Stripe payment processing endpoints in your FastAPI e-commerce backend.

## Available Endpoints

### 1. Create Payment Intent

```http
POST /api/v1/orders/create-payment-intent
```

Creates a Stripe Payment Intent which is required to process payments.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

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

**Response (200 OK):**
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

### 2. Create Order with Payment

```http
POST /api/v1/orders/create-order-with-payment
```

Creates an order and associated payment intent in one step. More efficient than creating them separately.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

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

**Response (200 OK):**
```json
{
  "order_id": "order_789",
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "amount": 29.99,
  "status": "requires_payment_method"
}
```

### 3. Confirm Payment

```http
POST /api/v1/orders/confirm-payment/{order_id}?payment_intent_id=pi_123
```

Confirms payment for an order and updates order status. Usually handled by webhooks, but can be triggered manually.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Payment confirmed successfully",
  "order_id": "order_789",
  "payment_status": "succeeded"
}
```

### 4. Process Refund (Admin only)

```http
POST /api/v1/orders/refund/{order_id}
```

Process a refund for an order (admin only).

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "payment_intent_id": "pi_1234567890",
  "refund_amount": 15.00  // optional, defaults to full amount
}
```

**Response (200 OK):**
```json
{
  "message": "Refund processed successfully",
  "refund_id": "re_1234567890",
  "amount": 15.00,
  "status": "succeeded"
}
```

### 5. Payment Methods

#### 5.1 Create Payment Method

```http
POST /api/v1/payment-methods
```

Create and save a new payment method for the current user.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "type": "card",
  "card_token": "tok_visa",
  "customer_id": "cus_1234567890",  // optional
  "is_default": true               // optional, set as default payment method
}
```

**Response (200 OK):**
```json
{
  "id": "pm_123",
  "type": "card",
  "card": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  },
  "customer": "cus_1234567890"
}
```

#### 5.2 Get Payment Methods

```http
GET /api/v1/payment-methods
```

Get all saved payment methods for the current user.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
[
  {
    "id": "pm_123",
    "type": "card",
    "card": {
      "brand": "visa",
      "last4": "4242",
      "exp_month": 12,
      "exp_year": 2025
    },
    "customer": "cus_1234567890"
  },
  {
    "id": "pm_456",
    "type": "card",
    "card": {
      "brand": "mastercard",
      "last4": "5555",
      "exp_month": 10,
      "exp_year": 2024
    },
    "customer": "cus_1234567890"
  }
]
```

#### 5.3 Get Payment Method by ID

```http
GET /api/v1/payment-methods/{payment_method_id}
```

Get details of a specific payment method.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "pm_123",
  "type": "card",
  "card": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  },
  "customer": "cus_1234567890"
}
```

#### 5.4 Delete Payment Method

```http
DELETE /api/v1/payment-methods/{payment_method_id}
```

Delete (deactivate) a payment method.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Payment method deleted successfully"
}
```

#### 5.5 Set Default Payment Method

```http
POST /api/v1/payment-methods/{payment_method_id}/set-default
```

Set a payment method as the default for the user.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "pm_123",
  "type": "card",
  "card": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  },
  "customer": "cus_1234567890",
  "is_default": true
}
```

### 6. Stripe Webhook Endpoint

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

## Integration Flow

### Basic One-Time Payment Flow

1. **Create Order with Payment Intent**
   - Call `/api/v1/orders/create-order-with-payment` with address details
   - Get back `client_secret` and `order_id`

2. **Process Payment with Stripe.js on Frontend**
   - Use `client_secret` with Stripe.js to collect and process payment
   - Handle success/failure on frontend

3. **Confirmation (handled by webhook)**
   - Webhook automatically updates order status when payment succeeds
   - Optional: Call confirm-payment endpoint manually if needed

### Saved Payment Methods Flow

1. **Create and Save Payment Method**
   - Call `/api/v1/payment-methods` to save a payment method
   - Store the returned payment method ID for future use

2. **Use Saved Payment Method**
   - Include `payment_method_id` when creating an order with payment
   - Set `save_payment_method: true` to save a new payment method during checkout

3. **Manage Payment Methods**
   - List, view, delete, or set a payment method as default
   - Use the default payment method automatically for future orders

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

## Deployment Checklist

1. Replace test API keys with live keys in production environment
2. Configure webhook endpoint in Stripe Dashboard
3. Set up monitoring for payment failures
4. Implement proper logging and alerting
5. Test the complete payment flow before going live
