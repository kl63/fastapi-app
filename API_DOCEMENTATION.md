# FreshCart E-Commerce API Documentation

This document outlines all the necessary API routes for a fully functioning e-commerce platform like FreshCart. The API follows RESTful conventions and includes authentication, product management, order processing, and more.

## Base URL
```
https://fastapi.kevinlinportfolio.com/freshcart/
```

## Authentication
All authenticated routes require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Authentication & User Management

### Register User
```http
POST /auth/register
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890"
}
```

### Login User
```http
POST /auth/login
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Refresh Token
```http
POST /auth/refresh
```
**Body:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

### Logout
```http
POST /auth/logout
```
**Headers:** `Authorization: Bearer <token>`

### Get User Profile
```http
GET /users/profile
```
**Headers:** `Authorization: Bearer <token>`

### Update User Profile
```http
PUT /users/profile
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890",
  "dateOfBirth": "1990-01-01"
}
```

### Change Password
```http
PUT /users/password
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "currentPassword": "oldpassword",
  "newPassword": "newpassword123"
}
```

### Forgot Password
```http
POST /auth/forgot-password
```
**Body:**
```json
{
  "email": "user@example.com"
}
```

### Reset Password
```http
POST /auth/reset-password
```
**Body:**
```json
{
  "token": "reset_token",
  "newPassword": "newpassword123"
}
```

---

## 2. User Addresses

### Get User Addresses
```http
GET /users/addresses
```
**Headers:** `Authorization: Bearer <token>`

### Add Address
```http
POST /users/addresses
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "type": "home", // "home", "work", "other"
  "firstName": "John",
  "lastName": "Doe",
  "street": "123 Main St",
  "city": "Anytown",
  "state": "ST",
  "zipCode": "12345",
  "country": "US",
  "phone": "+1234567890",
  "isDefault": true
}
```

### Update Address
```http
PUT /users/addresses/:addressId
```
**Headers:** `Authorization: Bearer <token>`

### Delete Address
```http
DELETE /users/addresses/:addressId
```
**Headers:** `Authorization: Bearer <token>`

---

## 3. Categories

### Get All Categories
```http
GET /categories
```
**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `parent` (optional): Parent category ID for subcategories

### Get Category by ID
```http
GET /categories/:categoryId
```

### Get Category by Slug
```http
GET /categories/slug/:slug
```

### Create Category (Admin)
```http
POST /categories
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "name": "Fresh Produce",
  "slug": "fresh-produce",
  "description": "Fresh fruits and vegetables",
  "icon": "🥬",
  "image": "category-image-url",
  "parentId": null,
  "isActive": true,
  "sortOrder": 1
}
```

### Update Category (Admin)
```http
PUT /categories/:categoryId
```
**Headers:** `Authorization: Bearer <admin_token>`

### Delete Category (Admin)
```http
DELETE /categories/:categoryId
```
**Headers:** `Authorization: Bearer <admin_token>`

---

## 4. Products

### Get All Products
```http
GET /products
```
**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `category` (optional): Category ID or slug
- `search` (optional): Search term
- `minPrice` (optional): Minimum price filter
- `maxPrice` (optional): Maximum price filter
- `inStock` (optional): true/false
- `isOrganic` (optional): true/false
- `isOnSale` (optional): true/false
- `sortBy` (optional): "price", "name", "rating", "newest"
- `sortOrder` (optional): "asc", "desc"

### Get Product by ID
```http
GET /products/:productId
```

### Get Product by Slug
```http
GET /products/slug/:slug
```

### Get Featured Products
```http
GET /products/featured
```

### Get Related Products
```http
GET /products/:productId/related
```

### Search Products
```http
GET /products/search
```
**Query Parameters:**
- `q`: Search query
- `category` (optional): Category filter
- `page` (optional): Page number
- `limit` (optional): Items per page

### Create Product (Admin)
```http
POST /products
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "name": "Organic Bananas",
  "slug": "organic-bananas",
  "description": "Fresh organic bananas",
  "price": 2.99,
  "originalPrice": 3.49,
  "sku": "ORG-BAN-001",
  "categoryId": "category-id",
  "images": ["image1.jpg", "image2.jpg"],
  "unit": "per bunch",
  "weight": "2 lbs",
  "isOrganic": true,
  "isOnSale": true,
  "isFeatured": false,
  "inStock": true,
  "stockQuantity": 100,
  "nutritionFacts": {
    "calories": 105,
    "protein": "1.3g",
    "carbs": "27g",
    "fat": "0.4g"
  },
  "tags": ["organic", "fresh", "fruit"],
  "isActive": true
}
```

### Update Product (Admin)
```http
PUT /products/:productId
```
**Headers:** `Authorization: Bearer <admin_token>`

### Delete Product (Admin)
```http
DELETE /products/:productId
```
**Headers:** `Authorization: Bearer <admin_token>`

### Update Product Stock (Admin)
```http
PATCH /products/:productId/stock
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "stockQuantity": 50,
  "inStock": true
}
```

---

## 5. Shopping Cart

### Get Cart
```http
GET /cart
```
**Headers:** `Authorization: Bearer <token>`

### Add Item to Cart
```http
POST /cart/items
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "productId": "product-id",
  "quantity": 2
}
```

### Update Cart Item
```http
PUT /cart/items/:itemId
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "quantity": 3
}
```

### Remove Cart Item
```http
DELETE /cart/items/:itemId
```
**Headers:** `Authorization: Bearer <token>`

### Clear Cart
```http
DELETE /cart
```
**Headers:** `Authorization: Bearer <token>`

### Apply Discount Code
```http
POST /cart/discount
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "code": "FRESH10"
}
```

### Remove Discount Code
```http
DELETE /cart/discount
```
**Headers:** `Authorization: Bearer <token>`

---

## 6. Wishlist

### Get Wishlist
```http
GET /wishlist
```
**Headers:** `Authorization: Bearer <token>`

### Add to Wishlist
```http
POST /wishlist/items
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "productId": "product-id"
}
```

### Remove from Wishlist
```http
DELETE /wishlist/items/:productId
```
**Headers:** `Authorization: Bearer <token>`

### Clear Wishlist
```http
DELETE /wishlist
```
**Headers:** `Authorization: Bearer <token>`

---

## 7. Orders

### Get User Orders
```http
GET /orders
```
**Headers:** `Authorization: Bearer <token>`
**Query Parameters:**
- `page` (optional): Page number
- `limit` (optional): Items per page
- `status` (optional): Order status filter

### Get Order by ID
```http
GET /orders/:orderId
```
**Headers:** `Authorization: Bearer <token>`

### Create Order
```http
POST /orders
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "deliveryAddressId": "address-id",
  "billingAddressId": "address-id",
  "paymentMethodId": "payment-method-id",
  "deliveryDate": "2024-12-16",
  "deliveryTimeSlot": "10:00-12:00",
  "specialInstructions": "Leave at door",
  "discountCode": "FRESH10"
}
```

### Cancel Order
```http
POST /orders/:orderId/cancel
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "reason": "Changed mind"
}
```

### Track Order
```http
GET /orders/:orderId/tracking
```
**Headers:** `Authorization: Bearer <token>`

### Get Order Invoice
```http
GET /orders/:orderId/invoice
```
**Headers:** `Authorization: Bearer <token>`

### Reorder
```http
POST /orders/:orderId/reorder
```
**Headers:** `Authorization: Bearer <token>`

---

## 8. Order Management (Admin)

### Get All Orders (Admin)
```http
GET /admin/orders
```
**Headers:** `Authorization: Bearer <admin_token>`
**Query Parameters:**
- `page`, `limit`, `status`, `customerId`, `dateFrom`, `dateTo`

### Update Order Status (Admin)
```http
PATCH /admin/orders/:orderId/status
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "status": "preparing", // "pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"
  "notes": "Order is being prepared"
}
```

### Assign Delivery (Admin)
```http
POST /admin/orders/:orderId/assign-delivery
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "driverId": "driver-id",
  "estimatedDeliveryTime": "2024-12-16T14:30:00Z"
}
```

---

## 9. Payment Methods

### Get Payment Methods
```http
GET /payment-methods
```
**Headers:** `Authorization: Bearer <token>`

### Add Payment Method
```http
POST /payment-methods
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "type": "card", // "card", "paypal", "apple_pay"
  "cardNumber": "4111111111111111",
  "expiryMonth": "12",
  "expiryYear": "2025",
  "cvv": "123",
  "cardholderName": "John Doe",
  "isDefault": true
}
```

### Update Payment Method
```http
PUT /payment-methods/:paymentMethodId
```
**Headers:** `Authorization: Bearer <token>`

### Delete Payment Method
```http
DELETE /payment-methods/:paymentMethodId
```
**Headers:** `Authorization: Bearer <token>`

---

## 10. Payments

### Process Payment
```http
POST /payments
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "orderId": "order-id",
  "paymentMethodId": "payment-method-id",
  "amount": 47.82
}
```

### Get Payment Status
```http
GET /payments/:paymentId
```
**Headers:** `Authorization: Bearer <token>`

### Refund Payment (Admin)
```http
POST /admin/payments/:paymentId/refund
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "amount": 47.82,
  "reason": "Customer request"
}
```

---

## 11. Reviews & Ratings

### Get Product Reviews
```http
GET /products/:productId/reviews
```
**Query Parameters:**
- `page`, `limit`, `rating` (filter by star rating)

### Add Product Review
```http
POST /products/:productId/reviews
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "rating": 5,
  "title": "Great product!",
  "comment": "Fresh and delicious bananas",
  "wouldRecommend": true
}
```

### Update Review
```http
PUT /reviews/:reviewId
```
**Headers:** `Authorization: Bearer <token>`

### Delete Review
```http
DELETE /reviews/:reviewId
```
**Headers:** `Authorization: Bearer <token>`

### Get User Reviews
```http
GET /users/reviews
```
**Headers:** `Authorization: Bearer <token>`

---

## 12. Notifications

### Get User Notifications
```http
GET /notifications
```
**Headers:** `Authorization: Bearer <token>`

### Mark Notification as Read
```http
PATCH /notifications/:notificationId/read
```
**Headers:** `Authorization: Bearer <token>`

### Mark All Notifications as Read
```http
PATCH /notifications/read-all
```
**Headers:** `Authorization: Bearer <token>`

### Delete Notification
```http
DELETE /notifications/:notificationId
```
**Headers:** `Authorization: Bearer <token>`

---

## 13. Coupons & Discounts

### Get Available Coupons
```http
GET /coupons
```
**Headers:** `Authorization: Bearer <token>`

### Validate Coupon
```http
POST /coupons/validate
```
**Headers:** `Authorization: Bearer <token>`
**Body:**
```json
{
  "code": "FRESH10",
  "cartTotal": 50.00
}
```

### Create Coupon (Admin)
```http
POST /admin/coupons
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "code": "FRESH10",
  "type": "percentage", // "percentage", "fixed_amount"
  "value": 10,
  "minimumOrderAmount": 25.00,
  "maxDiscountAmount": 50.00,
  "usageLimit": 1000,
  "userUsageLimit": 1,
  "validFrom": "2024-12-01T00:00:00Z",
  "validUntil": "2024-12-31T23:59:59Z",
  "isActive": true
}
```

---

## 14. Delivery & Shipping

### Get Delivery Zones
```http
GET /delivery/zones
```

### Check Delivery Availability
```http
POST /delivery/check-availability
```
**Body:**
```json
{
  "zipCode": "12345",
  "deliveryDate": "2024-12-16"
}
```

### Get Delivery Time Slots
```http
GET /delivery/time-slots
```
**Query Parameters:**
- `zipCode`, `date`

### Calculate Delivery Fee
```http
POST /delivery/calculate-fee
```
**Body:**
```json
{
  "zipCode": "12345",
  "cartTotal": 50.00,
  "deliveryDate": "2024-12-16"
}
```

---

## 15. Analytics & Reports (Admin)

### Get Dashboard Stats
```http
GET /admin/analytics/dashboard
```
**Headers:** `Authorization: Bearer <admin_token>`

### Get Sales Report
```http
GET /admin/analytics/sales
```
**Headers:** `Authorization: Bearer <admin_token>`
**Query Parameters:**
- `dateFrom`, `dateTo`, `groupBy` (day/week/month)

### Get Product Performance
```http
GET /admin/analytics/products
```
**Headers:** `Authorization: Bearer <admin_token>`

### Get Customer Analytics
```http
GET /admin/analytics/customers
```
**Headers:** `Authorization: Bearer <admin_token>`

---

## 16. Inventory Management (Admin)

### Get Inventory
```http
GET /admin/inventory
```
**Headers:** `Authorization: Bearer <admin_token>`

### Update Stock
```http
PATCH /admin/inventory/:productId
```
**Headers:** `Authorization: Bearer <admin_token>`
**Body:**
```json
{
  "stockQuantity": 100,
  "lowStockThreshold": 10
}
```

### Get Low Stock Items
```http
GET /admin/inventory/low-stock
```
**Headers:** `Authorization: Bearer <admin_token>`

---

## 17. Content Management

### Get Store Settings
```http
GET /settings/store
```

### Update Store Settings (Admin)
```http
PUT /admin/settings/store
```
**Headers:** `Authorization: Bearer <admin_token>`

### Get CMS Pages
```http
GET /pages
```

### Get Page by Slug
```http
GET /pages/:slug
```

### Create/Update Page (Admin)
```http
POST /admin/pages
PUT /admin/pages/:pageId
```
**Headers:** `Authorization: Bearer <admin_token>`

---

## 18. File Upload

### Upload Image
```http
POST /upload/image
```
**Headers:** `Authorization: Bearer <token>`
**Body:** `multipart/form-data`
```
file: <image_file>
folder: "products" // "products", "categories", "users"
```

### Delete Image
```http
DELETE /upload/image/:imageId
```
**Headers:** `Authorization: Bearer <token>`

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

### Common Error Codes:
- `VALIDATION_ERROR` - Input validation failed
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource already exists
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

## Rate Limiting

- **General API**: 1000 requests per hour per user
- **Authentication**: 10 requests per minute per IP
- **File Upload**: 50 requests per hour per user

---

## Webhooks

### Order Status Updates
```http
POST /webhooks/order-status
```

### Payment Notifications
```http
POST /webhooks/payment
```

### Inventory Alerts
```http
POST /webhooks/inventory
```

---

This API documentation provides a comprehensive foundation for building a fully functional e-commerce backend that supports all the features present in the FreshCart frontend application.