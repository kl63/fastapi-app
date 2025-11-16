# 🔐 Secure Stripe Payment Integration Guide

## ✅ Best Practice: Backend-Only Stripe Integration

This implementation follows **production-grade security practices** by keeping all Stripe secret keys in the FastAPI backend.

---

## 📋 Setup Instructions

### 1. Get Your Stripe API Keys

1. Go to https://dashboard.stripe.com/apikeys
2. Get your **Test Mode** keys:
   - `Publishable key` (pk_test_...) - Safe to expose to frontend
   - `Secret key` (sk_test_...) - ⚠️ **NEVER** expose to frontend!

### 2. Configure Your .env File

```bash
# Add to your .env file (NEVER commit this file to git!)
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here  # We'll get this later
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Restart Your FastAPI Server

```bash
python main.py
```

---

## 🚀 Payment Flow Architecture

### How It Works (The Right Way™)

```
1. Frontend (Next.js) → User adds items to cart
2. Frontend → POST /api/v1/orders (creates order)
3. Frontend → POST /api/v1/orders/{order_id}/create-payment-intent
4. Backend → Creates PaymentIntent with Stripe
5. Backend → Returns client_secret to frontend
6. Frontend → Uses client_secret with Stripe Elements
7. Stripe → Processes payment
8. Stripe → Sends webhook to backend
9. Backend → Updates order status automatically
```

### Why This Architecture?

✅ **Secret key stays on backend** - Impossible to steal
✅ **Full control** - Verify users, check inventory, prevent fraud
✅ **Automatic updates** - Webhooks update order status
✅ **Production-ready** - Same architecture used by major companies

---

## 📡 API Endpoints

### 1. Create Payment Intent

**POST** `/api/v1/orders/{order_id}/create-payment-intent`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxxxxxxxxx",
  "amount": 29.99,
  "currency": "usd"
}
```

### 2. Confirm Payment (Optional - Webhooks handle this automatically)

**POST** `/api/v1/orders/{order_id}/confirm-payment`

**Body:**
```json
{
  "payment_intent_id": "pi_xxxxxxxxxx"
}
```

### 3. Refund Payment (Admin Only)

**POST** `/api/v1/orders/{order_id}/refund?payment_intent_id=pi_xxx&amount=10.00`

---

## 💻 Frontend Integration (Next.js)

### Step 1: Install Stripe.js

```bash
npm install @stripe/stripe-js
```

### Step 2: Get Publishable Key from Backend

```typescript
// lib/stripe.ts
import { loadStripe } from '@stripe/stripe-js';

// Get publishable key from your backend (safe to expose)
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export default stripePromise;
```

### Step 3: Create Checkout Component

```typescript
// components/CheckoutForm.tsx
'use client';

import { useState } from 'react';
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js';

export default function CheckoutForm({ orderId }: { orderId: string }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);

    try {
      // Submit payment to Stripe
      const { error: submitError } = await elements.submit();
      if (submitError) {
        setError(submitError.message || 'Payment failed');
        setLoading(false);
        return;
      }

      // Confirm payment
      const { error: confirmError } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/order/${orderId}/success`,
        },
      });

      if (confirmError) {
        setError(confirmError.message || 'Payment failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <PaymentElement />
      
      {error && (
        <div className="text-red-500 text-sm">{error}</div>
      )}
      
      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg disabled:opacity-50"
      >
        {loading ? 'Processing...' : 'Pay Now'}
      </button>
    </form>
  );
}
```

### Step 4: Checkout Page

```typescript
// app/checkout/[orderId]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { Elements } from '@stripe/react-stripe-js';
import stripePromise from '@/lib/stripe';
import CheckoutForm from '@/components/CheckoutForm';

export default function CheckoutPage({ params }: { params: { orderId: string } }) {
  const [clientSecret, setClientSecret] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Create payment intent from backend
    const createPaymentIntent = async () => {
      try {
        const response = await fetch(
          `/api/v1/orders/${params.orderId}/create-payment-intent`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
          }
        );

        if (!response.ok) throw new Error('Failed to create payment intent');

        const data = await response.json();
        setClientSecret(data.client_secret);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    createPaymentIntent();
  }, [params.orderId]);

  if (loading) return <div>Loading...</div>;
  if (!clientSecret) return <div>Error loading payment</div>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Complete Your Payment</h1>
      
      <Elements
        stripe={stripePromise}
        options={{
          clientSecret,
          appearance: { theme: 'stripe' },
        }}
      >
        <CheckoutForm orderId={params.orderId} />
      </Elements>
    </div>
  );
}
```

---

## 🔔 Webhook Setup

### 1. Install Stripe CLI (For Testing)

```bash
brew install stripe/stripe-cli/stripe
stripe login
```

### 2. Forward Webhooks to Local Server

```bash
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

This will give you a webhook secret like: `whsec_xxxxx`

### 3. Add Webhook Secret to .env

```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### 4. Test a Payment

```bash
# Use test card
stripe trigger payment_intent.succeeded
```

### 5. Production Webhook Setup

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your URL: `https://your-api.com/api/v1/webhooks/stripe`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.refunded`
5. Copy the webhook secret to your production .env

---

## 🧪 Testing

### Test Cards

Stripe provides test cards for different scenarios:

| Card Number         | Scenario                    |
|---------------------|-----------------------------|
| 4242 4242 4242 4242 | ✅ Successful payment        |
| 4000 0000 0000 9995 | ❌ Insufficient funds        |
| 4000 0025 0000 3155 | 🔐 Requires authentication  |

- Use any future expiry date (e.g., 12/34)
- Use any 3-digit CVC

### Test API Endpoints

```bash
# 1. Create an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address_id": "xxx", "billing_address_id": "xxx"}'

# 2. Create payment intent
curl -X POST http://localhost:8000/api/v1/orders/{order_id}/create-payment-intent \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response includes client_secret for frontend
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep secret key on backend only
- Use environment variables
- Verify webhook signatures
- Validate user ownership of orders
- Use HTTPS in production
- Log all payment events

### ❌ DON'T:
- Never expose secret key to frontend
- Don't trust amounts from frontend
- Don't skip webhook signature verification
- Don't commit API keys to git
- Don't use test keys in production

---

## 📊 Order Status Flow

```
PENDING → (payment created) → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
        ↓ (payment failed)
      CANCELLED
        
CONFIRMED → (refund requested) → REFUNDED
```

---

## 🆘 Troubleshooting

### Issue: "No API key provided"
**Solution:** Make sure `STRIPE_SECRET_KEY` is set in your .env file

### Issue: "Invalid webhook signature"
**Solution:** Update `STRIPE_WEBHOOK_SECRET` in .env with the correct secret

### Issue: "Payment intent already confirmed"
**Solution:** Don't call confirm endpoint if using webhooks (webhooks handle this automatically)

### Issue: "Order not found"
**Solution:** Make sure the order belongs to the authenticated user

---

## 📚 Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Elements Guide](https://stripe.com/docs/payments/elements)
- [Webhook Best Practices](https://stripe.com/docs/webhooks/best-practices)
- [Test Cards](https://stripe.com/docs/testing)

---

## 🎉 You're Ready!

Your FastAPI backend now has production-grade Stripe integration with:

✅ Secure payment processing
✅ Automatic webhook handling  
✅ Refund support
✅ Full order lifecycle management

Start building your Next.js frontend and integrate with these secure backend endpoints!
