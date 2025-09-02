# Stripe Client Integration Guide

This document provides guidance on integrating with our Stripe payment processing API endpoints from client applications.

## Quick Reference

- **Save Payment Method**: `POST /api/v1/payment-methods/`
- **Process Payment with Saved Method**: `POST /api/v1/payments/process`
- **List Saved Payment Methods**: `GET /api/v1/payment-methods/`
- **Delete Payment Method**: `DELETE /api/v1/payment-methods/{id}`

## API Base URL

Your API is deployed at: `https://fastapi.kevinlinportfolio.com/api/v1`

## Authentication

All endpoints require JWT authentication using a Bearer token:

```
Authorization: Bearer <your_jwt_token>
```

To get a token, authenticate with the login endpoint:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=youremail@example.com&password=yourpassword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Payment Methods

### 1. Save a Payment Method

Use this endpoint to save a customer's payment method for future use. When a payment method is saved, the API automatically creates a Stripe Customer record (if one doesn't exist) and attaches the payment method to that customer. This is required for reusing payment methods:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/payment-methods" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "card",
    "card_token": "tok_visa",
    "is_default": true
  }'
```

Response:
```json
{
  "id": "pm_123",
  "type": "card",
  "card": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  }
}
```

### 2. List Saved Payment Methods

Retrieve all saved payment methods for a customer:

```bash
curl -X GET "https://fastapi.kevinlinportfolio.com/api/v1/payment-methods" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
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
    "is_default": true
  }
]
```

### 3. Set Default Payment Method

Make a specific payment method the default for a customer:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/payment-methods/pm_123/set-default" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
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
  "is_default": true
}
```

### 4. Delete Payment Method

Remove a saved payment method:

```bash
curl -X DELETE "https://fastapi.kevinlinportfolio.com/api/v1/payment-methods/pm_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "message": "Payment method deleted successfully"
}
```

## One-time Payment Flow

### 1. Create a Payment Intent

Use this endpoint to create a payment intent for a specified amount:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/orders/create-payment-intent" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 29.99,
    "currency": "usd",
    "metadata": {
      "product_id": "prod_123"
    }
  }'
```

Response:
```json
{
  "id": "pi_3RvGzVLu5Z15Sb321XLnrKKe",
  "client_secret": "pi_3RvGzVLu5Z15Sb321XLnrKKe_secret_abcdefghijklmnopqrstuvwxyz",
  "status": "requires_payment_method",
  "amount": 2999,
  "currency": "usd",
  "metadata": {
    "product_id": "prod_123",
    "user_id": "6d24bd4a-d613-4b24-8dc0-ffa923c467c9",
    "user_email": "user@example.com"
  }
}
```

### 2. Create Order with Payment Intent

Create an order and associated payment intent in one step:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/orders/create-order-with-payment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address_id": "addr_123",
    "billing_address_id": "addr_456",
    "notes": "Please handle with care"
  }'
```

Response:
```json
{
  "order_id": "order_789",
  "payment_intent_id": "pi_1234567890",
  "client_secret": "pi_1234567890_secret_xyz",
  "amount": 29.99,
  "status": "requires_payment_method"
}
```

### 3. Confirm Payment (After Frontend Processing)

After processing payment on the frontend with Stripe.js, confirm it on the backend:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/orders/confirm-payment/order_789?payment_intent_id=pi_1234567890" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "message": "Payment confirmed successfully",
  "order_id": "order_789",
  "payment_status": "succeeded"
}
```

### 4. Process Refund (Admin only)

For admins to process refunds:

```bash
curl -X POST "https://fastapi.kevinlinportfolio.com/api/v1/orders/refund/order_789" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_1234567890",
    "refund_amount": 15.00
  }'
```

Response:
```json
{
  "message": "Refund processed successfully",
  "refund_id": "re_1234567890",
  "amount": 15.00,
  "status": "succeeded"
}
```

## Important Notes on Stripe Customer Integration

Our API handles several important Stripe integrations automatically:

1. **Customer Creation**: When saving your first payment method, a Stripe Customer is automatically created
2. **Payment Method Attachment**: All saved payment methods are attached to your Stripe Customer
3. **Customer ID Passing**: When processing payments with saved methods, the Customer ID is automatically included

These features prevent common Stripe errors like:
- "PaymentMethod may not be used again" errors
- "PaymentMethod belongs to a Customer" errors
- Inability to use payment methods for off-session payments

## Implementation Steps

### 1. Frontend Setup with Stripe.js

Initialize Stripe in your frontend:

```javascript
// Get your publishable key from the API
const PUBLISHABLE_KEY = "pk_test_51OWJ8hLu5Z15Sb32FkzCS4tv7mfZnzAEqLStBnnVqYQb7vss0ysRV4chCGTRDyspcbYuh3lYZNNSUpznlAZY8LdF00qWwRnu2i";
const stripe = Stripe(PUBLISHABLE_KEY);

// Initialize Elements
const elements = stripe.elements();
const card = elements.create('card');
card.mount('#card-element');
```

### 2. Creating an Order with Payment Intent

```javascript
async function createOrderWithPayment(shippingAddressId, billingAddressId, notes = '', paymentMethodId = null, savePaymentMethod = false) {
  const response = await fetch('https://fastapi.kevinlinportfolio.com/api/v1/orders/create-order-with-payment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({
      shipping_address_id: shippingAddressId,
      billing_address_id: billingAddressId,
      notes,
      payment_method_id: paymentMethodId,
      save_payment_method: savePaymentMethod
    })
  });
  
  return await response.json();
}
```

### 3. Processing Payment

#### Option 1: One-time Payment

```javascript
async function processOneTimePayment(clientSecret, cardElement, saveCard = false) {
  try {
    const result = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
        billing_details: {
          name: 'Customer Name',
          email: 'customer@example.com'
        }
      },
      setup_future_usage: saveCard ? 'off_session' : undefined
    });
    
    if (result.error) {
      // Show error to your customer
      console.error(result.error.message);
      return { success: false, error: result.error.message };
    } else if (result.paymentIntent.status === 'succeeded') {
      // Payment succeeded
      return { success: true, paymentIntent: result.paymentIntent };
    }
  } catch (error) {
    console.error('Error processing payment:', error);
    return { success: false, error: error.message };
  }
}
```

#### Option 2: Using Saved Payment Method Flow

When using saved payment methods, they are automatically attached to a Stripe Customer record. This is required for off-session payments and reusing payment methods.

```javascript
async function processWithSavedPaymentMethod(clientSecret, paymentMethodId) {
  try {
    // The customer ID is automatically passed by the backend
    const result = await stripe.confirmCardPayment(clientSecret, {
      payment_method: paymentMethodId
    });
    
    if (result.error) {
      console.error(result.error.message);
      return { success: false, error: result.error.message };
    } else if (result.paymentIntent.status === 'succeeded') {
      return { success: true, paymentIntent: result.paymentIntent };
    }
  } catch (error) {
    console.error('Error processing payment:', error);
    return { success: false, error: error.message };
  }
}
```

### 4. Confirming Payment on Backend

```javascript
async function confirmPayment(orderId, paymentIntentId) {
  const response = await fetch(`https://fastapi.kevinlinportfolio.com/api/v1/orders/confirm-payment/${orderId}?payment_intent_id=${paymentIntentId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  return await response.json();
}
```

### 5. Managing Payment Methods

```javascript
// Save a new payment method
async function savePaymentMethod(cardElement, makeDefault = false) {
  try {
    // Create a token from card element
    const result = await stripe.createToken(cardElement);
    
    if (result.error) {
      return { success: false, error: result.error.message };
    }
    
    // Save the token to your backend
    const response = await fetch('https://fastapi.kevinlinportfolio.com/api/v1/payment-methods', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        type: 'card',
        card_token: result.token.id,
        is_default: makeDefault
      })
    });
    
    const data = await response.json();
    return { success: true, paymentMethod: data };
    
  } catch (error) {
    console.error('Error saving payment method:', error);
    return { success: false, error: error.message };
  }
}

// Get saved payment methods
async function getSavedPaymentMethods() {
  const response = await fetch('https://fastapi.kevinlinportfolio.com/api/v1/payment-methods', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  return await response.json();
}
```

## Testing

### Test Cards

Use these test card numbers for development:

- **Successful payment:** `4242 4242 4242 4242`
- **Payment requires authentication:** `4000 0025 0000 3155`
- **Payment is declined:** `4000 0000 0000 0002`

### Complete Test Flows

### Flow 1: One-time Payment

1. Create an order with payment intent
2. Use the client_secret with Stripe.js to collect payment details
3. Process the payment with Stripe.js
4. Handle the response (success/failure)
5. (Optional) Confirm payment on the backend

### Flow 2: Saved Payment Methods

1. Save a customer's payment method
2. List available payment methods and let customer choose
3. Create an order with payment intent, passing the payment_method_id
4. Process the payment using the saved payment method
5. Handle the response (success/failure)

## Security Best Practices

1. **Never expose your Stripe secret key** in client-side code
2. **Always use HTTPS** for API communication
3. **Validate all inputs** before sending to the API
4. **Handle errors gracefully** with user-friendly messages
5. **Implement proper loading states** during payment processing

## Webhook Setup (Backend)

Stripe webhooks are already configured on your backend to handle asynchronous payment events at:

```
https://fastapi.kevinlinportfolio.com/api/v1/webhooks/stripe
```

This endpoint processes:
- Payment success/failure notifications
- Refund events
- Dispute/chargeback events

## Production Deployment

When moving to production:

1. Update the Stripe publishable key to your live key
2. Ensure all API calls use HTTPS
3. Add proper error handling and logging
4. Test the complete payment flow before going live
5. Set up monitoring for payment failures
