# 🎨 Frontend Integration Guide - Next.js + Stripe

## Quick Overview: Payment Flow

```
User → Add to Cart → Checkout → Create Order → Get Payment Intent → Pay with Stripe → Success!
```

---

## 📦 Step 1: Install Dependencies

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

---

## 🔧 Step 2: Create Stripe Configuration

**File: `lib/stripe.ts`**

```typescript
import { loadStripe } from '@stripe/stripe-js';

// Replace with your Stripe PUBLISHABLE key (safe to expose)
// Get this from your backend or env variable
export const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);
```

**File: `.env.local`**

```bash
# Your FastAPI backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Stripe Publishable Key (SAFE to expose - starts with pk_)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51OWJ8hLu5Z15Sb32FkzCS4tv7mfZnzAEqLStBnnVqYQb7vss0ysRV4chCGTRDyspcbYuh3lYZNNSUpznlAZY8LdF00qWwRnu2i
```

---

## 💳 Step 3: Create Checkout Component

**File: `components/CheckoutForm.tsx`**

```typescript
'use client';

import { useState } from 'react';
import {
  useStripe,
  useElements,
  PaymentElement,
} from '@stripe/react-stripe-js';
import { useRouter } from 'next/navigation';

interface CheckoutFormProps {
  orderId: string;
  amount: number;
}

export default function CheckoutForm({ orderId, amount }: CheckoutFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const router = useRouter();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Submit the payment information to Stripe
      const { error: submitError } = await elements.submit();
      
      if (submitError) {
        setError(submitError.message || 'Payment failed');
        setLoading(false);
        return;
      }

      // Confirm the payment with Stripe
      const { error: confirmError } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/order/${orderId}/success`,
        },
      });

      if (confirmError) {
        setError(confirmError.message || 'Payment failed');
        setLoading(false);
      }
      
      // If no error, Stripe will redirect to return_url
      
    } catch (err) {
      setError('An unexpected error occurred');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-md mx-auto">
      {/* Stripe Payment Element - handles all payment methods */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <PaymentElement />
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Order summary */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Total Amount:</span>
          <span className="text-2xl font-bold">${amount.toFixed(2)}</span>
        </div>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={!stripe || loading}
        className={`
          w-full py-4 px-6 rounded-lg font-semibold text-white
          transition-all duration-200
          ${!stripe || loading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 active:scale-95'
          }
        `}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Processing...
          </span>
        ) : (
          `Pay $${amount.toFixed(2)}`
        )}
      </button>

      {/* Security badge */}
      <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
        </svg>
        Secure payment powered by Stripe
      </div>
    </form>
  );
}
```

---

## 🎯 Step 4: Create Checkout Page

**File: `app/checkout/[orderId]/page.tsx`**

```typescript
'use client';

import { useEffect, useState } from 'react';
import { Elements } from '@stripe/react-stripe-js';
import { stripePromise } from '@/lib/stripe';
import CheckoutForm from '@/components/CheckoutForm';
import { useParams } from 'next/navigation';

interface PaymentIntent {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

export default function CheckoutPage() {
  const params = useParams();
  const orderId = params.orderId as string;
  
  const [paymentIntent, setPaymentIntent] = useState<PaymentIntent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const createPaymentIntent = async () => {
      try {
        // Get JWT token from localStorage (or your auth solution)
        const token = localStorage.getItem('token');
        
        if (!token) {
          setError('Please login to continue');
          return;
        }

        // Call your FastAPI backend to create payment intent
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/orders/${orderId}/create-payment-intent`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to create payment intent');
        }

        const data = await response.json();
        setPaymentIntent(data);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    createPaymentIntent();
  }, [orderId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading payment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg max-w-md">
          <h3 className="font-semibold mb-2">Error</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!paymentIntent) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Complete Your Payment
          </h1>
          <p className="text-gray-600">
            Order ID: {orderId}
          </p>
        </div>

        {/* Payment Form */}
        <Elements
          stripe={stripePromise}
          options={{
            clientSecret: paymentIntent.client_secret,
            appearance: {
              theme: 'stripe',
              variables: {
                colorPrimary: '#2563eb',
              },
            },
          }}
        >
          <CheckoutForm
            orderId={orderId}
            amount={paymentIntent.amount}
          />
        </Elements>
      </div>
    </div>
  );
}
```

---

## ✅ Step 5: Create Success Page

**File: `app/order/[orderId]/success/page.tsx`**

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';

interface Order {
  id: string;
  order_number: string;
  status: string;
  total_amount: number;
}

export default function PaymentSuccessPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const orderId = params.orderId as string;
  
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  // Get payment intent from URL params
  const paymentIntent = searchParams.get('payment_intent');

  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const token = localStorage.getItem('token');
        
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/orders/${orderId}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setOrder(data);
        }
      } catch (err) {
        console.error('Error fetching order:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Success Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Success Icon */}
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg
              className="w-10 h-10 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          {/* Success Message */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h1>
          <p className="text-gray-600 mb-8">
            Thank you for your order. We've received your payment.
          </p>

          {/* Order Details */}
          {order && (
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <div className="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p className="text-sm text-gray-500">Order Number</p>
                  <p className="font-semibold">{order.order_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Amount Paid</p>
                  <p className="font-semibold">${order.total_amount.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <p className="font-semibold capitalize">{order.status}</p>
                </div>
                {paymentIntent && (
                  <div>
                    <p className="text-sm text-gray-500">Payment ID</p>
                    <p className="font-mono text-xs">{paymentIntent}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <Link
              href={`/orders/${orderId}`}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              View Order Details
            </Link>
            <Link
              href="/shop"
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Continue Shopping
            </Link>
          </div>
        </div>

        {/* What's Next */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">What's Next?</h3>
          <ul className="space-y-2 text-sm text-blue-700">
            <li>✉️ You'll receive an email confirmation shortly</li>
            <li>📦 Your order will be processed and shipped soon</li>
            <li>🔔 You'll get notifications about your order status</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
```

---

## 🔄 Complete User Flow

```
1. User browses products → Adds to cart
2. User clicks "Checkout"
3. App creates order via POST /api/v1/orders
4. App redirects to /checkout/[orderId]
5. Page calls POST /api/v1/orders/{orderId}/create-payment-intent
6. Backend returns client_secret
7. Stripe Elements loads with client_secret
8. User enters card details
9. User clicks "Pay"
10. Stripe processes payment
11. Redirect to /order/[orderId]/success
12. Webhook updates order status to "confirmed"
13. Show success message
```

---

## 🧪 Testing with Test Cards

In your Stripe Elements form, users can use these test cards:

| Card Number | Scenario |
|-------------|----------|
| 4242 4242 4242 4242 | ✅ Success |
| 4000 0000 0000 9995 | ❌ Decline (insufficient funds) |
| 4000 0025 0000 3155 | 🔐 Requires 3D Secure |

- Any future expiry date (e.g., 12/34)
- Any 3-digit CVC
- Any zip code

---

## 🎨 Styling Tips

The Stripe PaymentElement is fully customizable:

```typescript
<Elements
  stripe={stripePromise}
  options={{
    clientSecret: paymentIntent.client_secret,
    appearance: {
      theme: 'stripe', // or 'night', 'flat'
      variables: {
        colorPrimary: '#2563eb',
        colorBackground: '#ffffff',
        colorText: '#1f2937',
        colorDanger: '#ef4444',
        fontFamily: 'system-ui, sans-serif',
        spacingUnit: '4px',
        borderRadius: '8px',
      },
    },
  }}
>
```

---

## 🔐 Security Checklist

✅ **NEVER** put your Secret Key in frontend code  
✅ **ALWAYS** create PaymentIntents from your backend  
✅ **ALWAYS** verify webhooks with signature  
✅ **ALWAYS** use HTTPS in production  
✅ **NEVER** trust amount/price from frontend  

---

## 📱 Mobile Responsive

The Stripe PaymentElement is automatically mobile-responsive, but make sure your checkout page is too:

```tsx
<div className="min-h-screen bg-gray-50 py-4 sm:py-12 px-4">
  <div className="max-w-md sm:max-w-3xl mx-auto">
    {/* Your checkout form */}
  </div>
</div>
```

---

## 🚀 You're Ready!

Your payment flow is secure, production-ready, and follows Stripe's best practices!

Need help? Check:
- 📚 [Stripe Documentation](https://stripe.com/docs/payments/accept-a-payment)
- 🔧 [Stripe Elements](https://stripe.com/docs/stripe-js/react)
- 💬 [Your FastAPI logs](http://localhost:8000/docs)
