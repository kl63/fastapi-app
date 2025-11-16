# Import all models here so Alembic can detect them
from app.db.base_class import Base
from app.models.user import User
from app.models.address import Address
from app.models.category import Category
from app.models.product import Product
from app.models.cart import CartItem
from app.models.wishlist import WishlistItem
from app.models.order import Order, OrderItem, OrderStatusHistory
from app.models.review import Review
from app.models.notification import Notification
from app.models.coupon import Coupon
