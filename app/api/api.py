from fastapi import APIRouter

from app.api.endpoints import auth, users, categories, products, cart, wishlist, orders, addresses, reviews, coupons, notifications, webhooks

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["Addresses"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(cart.router, prefix="/cart", tags=["Shopping Cart"])
api_router.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders & Payments"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(coupons.router, prefix="/coupons", tags=["Coupons"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
