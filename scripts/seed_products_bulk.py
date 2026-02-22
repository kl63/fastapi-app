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

# Unsplash image collections by category
UNSPLASH_IMAGES = {
    "Fresh Produce": [
        "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6",
        "https://images.unsplash.com/photo-1540420773420-3366772f4999",
        "https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c"
    ],
    "Dairy & Eggs": [
        "https://images.unsplash.com/photo-1563636619-e9143da7973b",
        "https://images.unsplash.com/photo-1550583724-b2692b85b150"
    ],
    "Meat & Seafood": [
        "https://images.unsplash.com/photo-1603048297172-c92544798d5a",
        "https://images.unsplash.com/photo-1615485290382-441e4d049cb5"
    ],
    "Bakery": [
        "https://images.unsplash.com/photo-1509440159596-0249088772ff",
        "https://images.unsplash.com/photo-1555507036-ab1f4038808a"
    ],
    "Beverages": [
        "https://images.unsplash.com/photo-1600271886742-f049cd451bba",
        "https://images.unsplash.com/photo-1570831739435-6601aa3fa4fb"
    ],
    "default": [
        "https://images.unsplash.com/photo-1516594798947-e65505dbb29d",
        "https://images.unsplash.com/photo-1534080564583-6be75777b70a"
    ]
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


def generate_price() -> tuple:
    """Generate price and optional sale price"""
    base_price = round(random.uniform(1.99, 49.99), 2)
    
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
        while db.query(Product).filter(Product.slug == slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Check if product already exists
        existing = db.query(Product).filter(Product.slug == slug).first()
        if existing:
            continue
        
        # Generate prices
        price, original_price = generate_price()
        is_on_sale = original_price is not None
        
        # Generate other attributes (brand already generated above)
        is_organic = random.random() < 0.25
        is_featured = random.random() < 0.15
        stock_quantity = random.randint(10, 500)
        
        # Get image
        images = UNSPLASH_IMAGES.get(category_name, UNSPLASH_IMAGES["default"])
        image = random.choice(images)
        
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
