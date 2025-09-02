# Stripe Checkout Implementation Guide for Frontend Developers

## Overview

This document provides implementation details for integrating our Stripe payment processing API with your frontend application. The checkout flow is designed to support both one-time payments and saved payment methods.

## API Endpoints

**Base URL**: `https://fastapi.kevinlinportfolio.com/api/v1`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orders/create-payment-intent` | POST | Create a payment intent for a specific amount |
| `/orders/create-order-with-payment` | POST | Create an order with payment in one step |
| `/orders/confirm-payment/{order_id}` | POST | Confirm a payment after frontend processing |
| `/payment-methods/` | GET | List user's saved payment methods |
| `/payment-methods/` | POST | Save a new payment method |
| `/payment-methods/{id}/set-default` | POST | Set a payment method as default |
| `/payment-methods/{id}` | DELETE | Delete a saved payment method |

## Required Dependencies

```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

## Initial Setup

```javascript
// 1. Import Stripe dependencies
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement } from '@stripe/react-stripe-js';

// 2. Initialize Stripe with your publishable key
const stripePromise = loadStripe('pk_test_51OWJ8hLu5Z15Sb32FkzCS4tv7mfZnzAEqLStBnnVqYQb7vss0ysRV4chCGTRDyspcbYuh3lYZNNSUpznlAZY8LdF00qWwRnu2i');

// 3. Wrap your checkout component with Elements provider
function CheckoutPage() {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm />
    </Elements>
  );
}
```

## Checkout Component Implementation

```jsx
import React, { useState, useEffect } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { api } from '../services/api';

function CheckoutForm({ amount, currency = 'usd', metadata = {}, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [savedPaymentMethods, setSavedPaymentMethods] = useState([]);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(null);
  const [saveCard, setSaveCard] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  // Fetch saved payment methods when component loads
  useEffect(() => {
    async function fetchPaymentMethods() {
      try {
        const response = await api.get('/payment-methods/');
        setSavedPaymentMethods(response.data);
      } catch (err) {
        console.error('Error fetching payment methods:', err);
      }
    }
    fetchPaymentMethods();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setIsProcessing(true);

    try {
      // 1. Create payment intent on the server
      const paymentIntentResponse = await api.post('/orders/create-payment-intent', {
        amount,
        currency,
        metadata
      });
      
      const { client_secret } = paymentIntentResponse.data;
      let result;

      // 2. Confirm payment with Stripe.js
      if (selectedPaymentMethod) {
        // Using saved payment method
        result = await stripe.confirmCardPayment(client_secret, {
          payment_method: selectedPaymentMethod.id
        });
      } else {
        // Using new card
        const cardElement = elements.getElement(CardElement);
        
        result = await stripe.confirmCardPayment(client_secret, {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: document.getElementById('card-holder-name').value,
            }
          },
          setup_future_usage: saveCard ? 'off_session' : undefined
        });
      }

      // 3. Handle result
      if (result.error) {
        setError(result.error.message);
      } else if (result.paymentIntent.status === 'succeeded') {
        // Payment successful
        onSuccess && onSuccess(result.paymentIntent);
      }
    } catch (err) {
      setError(err.message || 'An error occurred during payment processing');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Customer name field */}
      <div className="form-group">
        <label htmlFor="card-holder-name">Name on card</label>
        <input id="card-holder-name" className="form-control" required />
      </div>

      {/* Saved payment methods */}
      {savedPaymentMethods.length > 0 && (
        <div className="saved-payment-methods">
          <h4>Saved Payment Methods</h4>
          {savedPaymentMethods.map(method => (
            <div key={method.id} className="saved-payment-method">
              <input
                type="radio"
                id={`method-${method.id}`}
                name="paymentMethod"
                onChange={() => setSelectedPaymentMethod(method)}
              />
              <label htmlFor={`method-${method.id}`}>
                {method.card.brand} ending in {method.card.last4} (expires {method.card.exp_month}/{method.card.exp_year})
              </label>
            </div>
          ))}
          <div className="new-card-option">
            <input
              type="radio"
              id="new-card"
              name="paymentMethod"
              onChange={() => setSelectedPaymentMethod(null)}
              defaultChecked
            />
            <label htmlFor="new-card">Use a new card</label>
          </div>
        </div>
      )}

      {/* Only show card element if no saved method is selected */}
      {!selectedPaymentMethod && (
        <div className="form-group">
          <label>Card details</label>
          <CardElement 
            className="card-element" 
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#424770',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
                invalid: {
                  color: '#9e2146',
                },
              },
            }}
          />
          <div className="save-card-option">
            <input
              type="checkbox"
              id="save-card"
              checked={saveCard}
              onChange={() => setSaveCard(!saveCard)}
            />
            <label htmlFor="save-card">Save this card for future purchases</label>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && <div className="alert alert-danger">{error}</div>}

      {/* Submit button */}
      <button 
        type="submit" 
        className="pay-button" 
        disabled={!stripe || isProcessing}
      >
        {isProcessing ? 'Processing...' : `Pay $${amount.toFixed(2)}`}
      </button>
    </form>
  );
}
```

## Integration with Order Creation

For a complete checkout flow that includes order creation:

```javascript
async function createOrderWithPayment(shippingAddressId, billingAddressId, notes = '') {
  try {
    // 1. Create order with payment intent
    const orderResponse = await api.post('/orders/create-order-with-payment', {
      shipping_address_id: shippingAddressId,
      billing_address_id: billingAddressId,
      notes
    });
    
    const { order_id, payment_intent_id, client_secret } = orderResponse.data;
    
    // 2. Process payment with Stripe Elements
    const result = await stripe.confirmCardPayment(client_secret, {
      payment_method: {
        card: elements.getElement(CardElement),
        billing_details: {
          name: document.getElementById('card-holder-name').value,
        }
      }
    });
    
    if (result.error) {
      throw new Error(result.error.message);
    }
    
    // 3. Confirm payment on backend
    await api.post(`/orders/confirm-payment/${order_id}?payment_intent_id=${payment_intent_id}`);
    
    return {
      success: true,
      order_id,
      payment_intent_id
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}
```

## Error Handling

Common Stripe error codes and how to handle them:

| Error Code | Description | Handling Strategy |
|------------|-------------|-------------------|
| `card_declined` | Card was declined | Show message asking for different payment method |
| `insufficient_funds` | Insufficient funds | Suggest using a different card |
| `expired_card` | Card is expired | Ask for a different card |
| `authentication_required` | 3D Secure required | Handle with 3D Secure flow |

Example error handling:

```javascript
try {
  // Payment code here
} catch (error) {
  switch(error.code) {
    case 'card_declined':
      showError('Your card was declined. Please try a different card.');
      break;
    case 'expired_card':
      showError('Your card is expired. Please try a different card.');
      break;
    // Handle other specific errors
    default:
      showError('An error occurred while processing your payment. Please try again.');
  }
}
```

## Testing

Use these test card numbers:

- Successful payment: `4242 4242 4242 4242`
- Requires authentication: `4000 0025 0000 3155`
- Payment declined: `4000 0000 0000 0002`

Use any future expiration date, any 3-digit CVC, and any postal code.

## Important Notes on Stripe Customer Integration

Our API handles several important features automatically:

1. **Customer Creation**: When saving a payment method, a Stripe Customer is automatically created
2. **Payment Method Attachment**: All saved payment methods are attached to your Stripe Customer
3. **Customer ID Passing**: When processing payments with saved methods, the Customer ID is automatically included

This prevents common Stripe errors like:
- "PaymentMethod may not be used again" errors
- "PaymentMethod belongs to a Customer" errors
- Inability to use payment methods for off-session payments

## Additional Resources

- [Stripe.js Documentation](https://stripe.com/docs/js)
- [Stripe Elements](https://stripe.com/docs/stripe-js/react)
- [Payment Intents API](https://stripe.com/docs/api/payment_intents)
- [Handle 3D Secure](https://stripe.com/docs/payments/3d-secure)
