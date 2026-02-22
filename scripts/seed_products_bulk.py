"""
Bulk seed script to populate database with 1000+ products
Usage: python scripts/seed_products_bulk.py
"""
import sys
import os
from pathlib import Path
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.product import Product
import uuid
from datetime import datetime


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name"""
    slug = name.lower().replace(' ', '-').replace('&', 'and')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug


# Product templates by category
PRODUCT_TEMPLATES = {
    "Fresh Produce": {
        "fruits": [
            "Apple", "Banana", "Orange", "Grape", "Strawberry", "Blueberry", "Raspberry",
            "Mango", "Pineapple", "Watermelon", "Cantaloupe", "Honeydew", "Peach", "Plum",
            "Cherry", "Kiwi", "Papaya", "Guava", "Lychee", "Dragon Fruit", "Passion Fruit",
            "Persimmon", "Pomegranate", "Grapefruit", "Lemon", "Lime", "Tangerine", "Pear",
            "Apricot", "Nectarine", "Blackberry", "Fig", "Date"
        ],
        "vegetables": [
            "Carrot", "Broccoli", "Cauliflower", "Spinach", "Lettuce", "Kale", "Cabbage",
            "Tomato", "Cucumber", "Bell Pepper", "Zucchini", "Eggplant", "Asparagus",
            "Green Bean", "Pea", "Corn", "Potato", "Sweet Potato", "Onion", "Garlic",
            "Celery", "Radish", "Beet", "Turnip", "Parsnip", "Brussels Sprout", "Artichoke",
            "Mushroom", "Squash", "Pumpkin"
        ],
        "herbs": [
            "Basil", "Cilantro", "Parsley", "Mint", "Rosemary", "Thyme", "Oregano",
            "Dill", "Sage", "Chives"
        ]
    },
    "Dairy & Eggs": {
        "types": [
            "Whole Milk", "2% Milk", "Skim Milk", "Almond Milk", "Oat Milk", "Soy Milk",
            "Heavy Cream", "Half and Half", "Butter", "Margarine", "Yogurt", "Greek Yogurt",
            "Cottage Cheese", "Cream Cheese", "Sour Cream", "Cheddar Cheese", "Mozzarella",
            "Parmesan", "Swiss Cheese", "Provolone", "Gouda", "Brie", "Feta", "Blue Cheese",
            "Eggs", "Egg Whites"
        ]
    },
    "Meat & Seafood": {
        "meats": [
            "Chicken Breast", "Chicken Thigh", "Ground Beef", "Beef Steak", "Pork Chop",
            "Bacon", "Sausage", "Ham", "Turkey Breast", "Ground Turkey", "Lamb Chop",
            "Veal Cutlet", "Duck Breast"
        ],
        "seafood": [
            "Salmon", "Tuna", "Cod", "Tilapia", "Shrimp", "Crab", "Lobster", "Scallops",
            "Mussels", "Clams", "Oysters", "Catfish", "Halibut", "Swordfish", "Snapper"
        ]
    },
    "Bakery": {
        "breads": [
            "White Bread", "Wheat Bread", "Sourdough", "Rye Bread", "Multigrain Bread",
            "Baguette", "Ciabatta", "Focaccia", "Pita Bread", "Naan", "Bagel", "English Muffin",
            "Croissant", "Danish Pastry", "Donut", "Muffin", "Scone", "Brownie", "Cookie"
        ]
    },
    "Beverages": {
        "types": [
            "Orange Juice", "Apple Juice", "Grape Juice", "Cranberry Juice", "Tomato Juice",
            "Lemonade", "Iced Tea", "Green Tea", "Coffee", "Soda", "Sparkling Water",
            "Coconut Water", "Energy Drink", "Sports Drink", "Vitamin Water"
        ]
    },
    "Pantry Staples": {
        "types": [
            "Pasta", "Rice", "Quinoa", "Couscous", "Flour", "Sugar", "Salt", "Pepper",
            "Olive Oil", "Vegetable Oil", "Vinegar", "Soy Sauce", "Ketchup", "Mustard",
            "Mayo", "Hot Sauce", "BBQ Sauce", "Honey", "Maple Syrup", "Peanut Butter",
            "Jam", "Jelly", "Canned Tomato", "Canned Bean", "Canned Soup", "Cereal",
            "Oatmeal", "Granola", "Crackers", "Chips"
        ]
    },
    "Snacks & Sweets": {
        "types": [
            "Potato Chips", "Tortilla Chips", "Pretzels", "Popcorn", "Nuts", "Trail Mix",
            "Granola Bar", "Energy Bar", "Candy Bar", "Chocolate", "Gummy Bears", "Lollipop",
            "Hard Candy", "Mints", "Gum", "Cookies", "Crackers", "Rice Cakes"
        ]
    },
    "Frozen Foods": {
        "types": [
            "Frozen Pizza", "Frozen Burrito", "Frozen Dinner", "Frozen Vegetable",
            "Frozen Fruit", "Ice Cream", "Frozen Yogurt", "Popsicle", "Frozen Waffle",
            "Frozen French Fries", "Frozen Chicken Nuggets", "Frozen Fish Sticks"
        ]
    }
}

# Adjectives to create variety
ADJECTIVES = [
    "Organic", "Fresh", "Premium", "Natural", "Local", "Farm-Fresh", "Artisan",
    "Gourmet", "Free-Range", "Grass-Fed", "Wild-Caught", "Sustainably Sourced",
    "Hand-Picked", "Vine-Ripened", "Sun-Dried", "Stone-Ground", "Cold-Pressed",
    "Extra Virgin", "Aged", "Smoked", "Roasted", "Raw", "Whole", "Sliced",
    "Diced", "Chopped", "Shredded", "Crumbled"
]

# Brands
BRANDS = [
    "Farm Fresh", "Nature's Best", "Organic Valley", "Green Fields", "Pure Harvest",
    "Golden Farms", "Sunrise", "Valley Fresh", "Mountain Peak", "Coastal Catch",
    "Prairie Pride", "Harvest Moon", "Blue Sky", "Red Rock", "Silver Creek"
]

# Product-specific Unsplash images
PRODUCT_IMAGES = {
    # Fruits
    "Apple": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb",
    "Banana": "https://images.unsplash.com/photo-1603833665858-e61d17a86224",
    "Orange": "https://images.unsplash.com/photo-1580052614034-c55d20bfee3b",
    "Grape": "https://images.unsplash.com/photo-1599819177950-30f6505535e0",
    "Strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6",
    "Blueberry": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e",
    "Mango": "https://images.unsplash.com/photo-1553279791-38f4b3f6094f",
    "Watermelon": "https://images.unsplash.com/photo-1589984662646-e7b2e4962f18",
    "Pineapple": "https://images.unsplash.com/photo-1550258987-190a2d41a8ba",
    "Avocado": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578",
    # Vegetables
    "Carrot": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37",
    "Broccoli": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc",
    "Tomato": "https://images.unsplash.com/photo-1546470427-1d9fcc4a1a2a",
    "Lettuce": "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1",
    "Spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb",
    "Potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655",
    "Onion": "https://images.unsplash.com/photo-1587049352846-4a222e784098",
    # Dairy
    "Milk": "https://images.unsplash.com/photo-1550583724-b2692b85b150",
    "Cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d",
    "Yogurt": "https://images.unsplash.com/photo-1488477181946-6428a0291777",
    "Butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d",
    "Eggs": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f",
    # Meat & Seafood
    "Chicken": "https://images.unsplash.com/photo-1604503468506-a8da13d82791",
    "Beef": "https://images.unsplash.com/photo-1603048297172-c92544798d5a",
    "Pork": "https://images.unsplash.com/photo-1602470520998-f4a52199a3d6",
    "Salmon": "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6",
    "Shrimp": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47",
    # Bakery
    "Bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff",
    "Bagel": "https://images.unsplash.com/photo-1551106652-a5bcf4b29f60",
    "Croissant": "https://images.unsplash.com/photo-1555507036-ab1f4038808a",
    "Muffin": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa",
    "Cookie": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35",
    # Beverages
    "Juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba",
    "Coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
    "Tea": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9",
    "Soda": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e",
    "Water": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d",
}

# Price ranges by product type (min, max)
PRICE_RANGES = {
    # Fruits - typically $0.99 - $6.99
    "Apple": (0.99, 4.99), "Banana": (0.49, 2.99), "Orange": (0.99, 5.99),
    "Grape": (2.99, 6.99), "Strawberry": (2.99, 6.99), "Blueberry": (3.99, 7.99),
    "Mango": (1.49, 4.99), "Watermelon": (4.99, 9.99), "Pineapple": (2.99, 5.99),
    "Avocado": (0.99, 3.99),
    # Vegetables - typically $0.99 - $5.99
    "Carrot": (1.49, 3.99), "Broccoli": (1.99, 4.99), "Tomato": (1.99, 5.99),
    "Lettuce": (1.49, 3.99), "Spinach": (2.49, 4.99), "Potato": (2.99, 6.99),
    "Onion": (1.49, 3.99),
    # Dairy - typically $2.99 - $8.99
    "Milk": (3.49, 6.99), "Cheese": (3.99, 9.99), "Yogurt": (3.99, 7.99),
    "Butter": (3.99, 6.99), "Eggs": (3.99, 7.99), "Cream": (2.99, 5.99),
    # Meat - typically $5.99 - $24.99
    "Chicken": (5.99, 14.99), "Beef": (8.99, 24.99), "Pork": (6.99, 16.99),
    "Turkey": (7.99, 16.99), "Lamb": (12.99, 29.99),
    # Seafood - typically $8.99 - $29.99
    "Salmon": (12.99, 24.99), "Shrimp": (9.99, 19.99), "Tuna": (8.99, 18.99),
    "Cod": (9.99, 16.99),
    # Bakery - typically $2.49 - $6.99
    "Bread": (2.49, 5.99), "Bagel": (2.99, 5.99), "Croissant": (2.99, 6.99),
    "Muffin": (2.49, 4.99), "Cookie": (3.99, 7.99), "Donut": (3.99, 6.99),
    # Beverages - typically $1.99 - $8.99
    "Juice": (2.99, 7.99), "Coffee": (5.99, 12.99), "Tea": (2.99, 8.99),
    "Soda": (1.99, 5.99), "Water": (0.99, 4.99),
    # Pantry - typically $1.99 - $9.99
    "Pasta": (1.99, 4.99), "Rice": (3.99, 9.99), "Cereal": (3.49, 6.99),
    "Oil": (4.99, 12.99), "Sauce": (2.99, 6.99),
}


def generate_product_name(category_name: str, base_name: str, brand: str = None) -> str:
    """Generate varied product names with realistic variations"""
    variations = []
    
    # Size variations
    sizes = ["Small", "Medium", "Large", "Family Size", "Value Pack", "Single Serve", 
             "12 oz", "16 oz", "32 oz", "1 lb", "2 lb", "5 lb", "1 Gallon", "Half Gallon"]
    
    # Packaging variations
    packaging = ["Pack of 6", "Pack of 12", "Bundle", "Twin Pack", "Triple Pack"]
    
    # Quality variations
    quality = ["Premium", "Select", "Choice", "Grade A", "Extra"]
    
    # Build variations
    if brand:
        variations.append(f"{brand} {base_name}")
        if random.random() > 0.5:
            size = random.choice(sizes)
            variations.append(f"{brand} {base_name} - {size}")
    
    # Add size variation
    if random.random() > 0.4:
        size = random.choice(sizes)
        variations.append(f"{base_name} - {size}")
    
    # Add packaging variation
    if random.random() > 0.6:
        pack = random.choice(packaging)
        variations.append(f"{base_name} {pack}")
    
    # Add quality variation
    if random.random() > 0.5:
        qual = random.choice(quality)
        variations.append(f"{qual} {base_name}")
    
    # Add adjective variation
    if random.random() > 0.5:
        adjective = random.choice(ADJECTIVES)
        variations.append(f"{adjective} {base_name}")
    
    # Default
    variations.append(base_name)
    
    return random.choice(variations)


def get_product_image(base_name: str) -> str:
    """Get product-specific image URL"""
    # Check for exact match first
    if base_name in PRODUCT_IMAGES:
        return PRODUCT_IMAGES[base_name]
    
    # Check for partial matches (e.g., "Whole Milk" matches "Milk")
    for key in PRODUCT_IMAGES:
        if key in base_name or base_name in key:
            return PRODUCT_IMAGES[key]
    
    # Default to a generic grocery image
    return "https://images.unsplash.com/photo-1534080564583-6be75777b70a"


def generate_description(product_name: str, category_name: str) -> str:
    """Generate product description"""
    descriptions = [
        f"Premium quality {product_name.lower()} sourced from trusted suppliers.",
        f"Fresh {product_name.lower()} perfect for your daily needs.",
        f"High-quality {product_name.lower()} at an affordable price.",
        f"Delicious {product_name.lower()} that your family will love.",
        f"Farm-fresh {product_name.lower()} delivered to your door.",
        f"Natural {product_name.lower()} with no artificial additives.",
        f"Carefully selected {product_name.lower()} for exceptional taste.",
        f"Top-grade {product_name.lower()} perfect for any meal.",
    ]
    return random.choice(descriptions)


def generate_price(base_name: str) -> tuple:
    """Generate realistic price based on product type and optional sale price"""
    # Get price range for this product, or use default
    price_range = PRICE_RANGES.get(base_name, (2.99, 12.99))
    base_price = round(random.uniform(price_range[0], price_range[1]), 2)
    
    # 30% chance of being on sale
    if random.random() < 0.3:
        discount = random.uniform(0.10, 0.40)
        sale_price = round(base_price * (1 - discount), 2)
        return sale_price, base_price
    
    return base_price, None


def seed_bulk_products(db: Session, num_products: int = 1000):
    """Generate and seed bulk products"""
    
    print(f"\n🔍 Fetching existing categories...")
    categories = db.query(Category).all()
    
    if not categories:
        print("❌ No categories found. Please run seed_products.py first to create categories.")
        return
    
    print(f"✅ Found {len(categories)} categories")
    
    # Create category map
    category_map = {cat.name: cat.id for cat in categories}
    
    print(f"\n📦 Generating {num_products} products...")
    
    products_created = 0
    batch_size = 100
    products_batch = []
    used_slugs = set()  # Track slugs to prevent duplicates
    
    for i in range(num_products):
        # Select random category
        category_name = random.choice(list(PRODUCT_TEMPLATES.keys()))
        
        # Get product templates for this category
        templates = PRODUCT_TEMPLATES.get(category_name, {})
        
        # Select random product type
        if templates:
            type_key = random.choice(list(templates.keys()))
            base_name = random.choice(templates[type_key])
        else:
            base_name = f"Product {i+1}"
        
        # Generate brand first
        brand = random.choice(BRANDS) if random.random() > 0.3 else None
        
        # Generate product name with realistic variations
        product_name = generate_product_name(category_name, base_name, brand)
        slug = create_slug(product_name)
        
        # Add unique suffix to slug if needed for uniqueness
        original_slug = slug
        counter = 1
        while slug in used_slugs or db.query(Product).filter(Product.slug == slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Add slug to used set
        used_slugs.add(slug)
        
        # Generate realistic prices based on product type
        price, original_price = generate_price(base_name)
        is_on_sale = original_price is not None
        
        # Generate other attributes (brand already generated above)
        is_organic = random.random() < 0.25
        is_featured = random.random() < 0.15
        stock_quantity = random.randint(10, 500)
        
        # Get product-specific image
        image = get_product_image(base_name)
        
        # Create product
        product = Product(
            id=str(uuid.uuid4()),
            name=product_name,
            slug=slug,
            description=generate_description(product_name, category_name),
            short_description=f"Quality {base_name.lower()} for everyday use",
            price=price,
            original_price=original_price,
            sku=f"SKU-{str(uuid.uuid4())[:8].upper()}",
            category_id=category_map.get(category_name),
            brand=brand,
            unit="each" if random.random() > 0.5 else "lb",
            weight=f"{random.uniform(0.5, 5):.1f} lb" if random.random() > 0.5 else None,
            images=[image, image, image],
            thumbnail=image,
            is_organic=is_organic,
            is_featured=is_featured,
            is_on_sale=is_on_sale,
            is_active=True,
            in_stock=stock_quantity > 0,
            stock_quantity=stock_quantity,
            low_stock_threshold=10,
            cost_price=round(price * 0.6, 2),
            view_count=random.randint(0, 1000),
            purchase_count=random.randint(0, 500),
            rating_average=round(random.uniform(3.5, 5.0), 1),
            rating_count=random.randint(0, 200),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        products_batch.append(product)
        products_created += 1
        
        # Batch insert for performance
        if len(products_batch) >= batch_size:
            db.bulk_save_objects(products_batch)
            db.commit()
            print(f"  ✓ Created {products_created}/{num_products} products...")
            products_batch = []
    
    # Insert remaining products
    if products_batch:
        db.bulk_save_objects(products_batch)
        db.commit()
    
    print(f"\n✅ Successfully created {products_created} products!")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("🚀 BULK SEEDING DATABASE WITH 1000+ PRODUCTS")
    print("=" * 60)
    
    num_products = int(input("\nHow many products to generate? (default: 1000): ") or "1000")
    
    print(f"\n⚠️  WARNING: This will create {num_products} products in your database!")
    confirmation = input("Type 'YES' to proceed: ")
    
    if confirmation != 'YES':
        print("\n❌ Aborted by user")
        return
    
    db = SessionLocal()
    
    try:
        seed_bulk_products(db, num_products)
        print("\n" + "=" * 60)
        print("🎉 BULK SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
