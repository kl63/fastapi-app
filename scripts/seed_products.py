"""
Seed script to populate database with sample categories and products
Usage: python scripts/seed_products.py
"""
import sys
import os
from pathlib import Path

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
    return name.lower().replace(' ', '-').replace('&', 'and')


def seed_categories(db: Session):
    """Create product categories"""
    categories_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Fresh Produce",
            "slug": "fresh-produce",
            "description": "Fresh fruits and vegetables",
            "icon": "🥬",
            "is_featured": True,
            "sort_order": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dairy & Eggs",
            "slug": "dairy-eggs",
            "description": "Milk, cheese, yogurt, and eggs",
            "icon": "🥛",
            "is_featured": True,
            "sort_order": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Meat & Seafood",
            "slug": "meat-seafood",
            "description": "Fresh and frozen meat and seafood",
            "icon": "🥩",
            "is_featured": True,
            "sort_order": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bakery",
            "slug": "bakery",
            "description": "Fresh bread, pastries, and baked goods",
            "icon": "🍞",
            "is_featured": True,
            "sort_order": 4
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Beverages",
            "slug": "beverages",
            "description": "Drinks, juices, and refreshments",
            "icon": "🥤",
            "is_featured": True,
            "sort_order": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pantry Staples",
            "slug": "pantry-staples",
            "description": "Pasta, rice, canned goods, and essentials",
            "icon": "🥫",
            "is_featured": False,
            "sort_order": 6
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Snacks & Sweets",
            "slug": "snacks-sweets",
            "description": "Chips, cookies, candy, and treats",
            "icon": "🍪",
            "is_featured": False,
            "sort_order": 7
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Frozen Foods",
            "slug": "frozen-foods",
            "description": "Frozen meals, vegetables, and desserts",
            "icon": "🧊",
            "is_featured": False,
            "sort_order": 8
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Health & Beauty",
            "slug": "health-beauty",
            "description": "Personal care and beauty products",
            "icon": "💄",
            "is_featured": False,
            "sort_order": 9
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Household",
            "slug": "household",
            "description": "Cleaning supplies and household items",
            "icon": "🧹",
            "is_featured": False,
            "sort_order": 10
        }
    ]
    
    category_map = {}
    
    for cat_data in categories_data:
        # Check if category already exists
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if existing:
            print(f"Category '{cat_data['name']}' already exists, skipping...")
            category_map[cat_data["slug"]] = existing.id
            continue
        
        category = Category(**cat_data)
        db.add(category)
        category_map[cat_data["slug"]] = cat_data["id"]
        print(f"Created category: {cat_data['name']}")
    
    db.commit()
    return category_map


def seed_products(db: Session, category_map: dict):
    """Create sample products"""
    products_data = [
        # Fresh Produce
        {
            "name": "Organic Bananas",
            "description": "Sweet and naturally ripened organic bananas. Perfect for smoothies, baking, or a healthy snack.",
            "short_description": "Sweet organic bananas",
            "price": 2.99,
            "original_price": 3.49,
            "cost_price": 1.50,
            "sku": "PROD-BAN-001",
            "category_slug": "fresh-produce",
            "brand": "Organic Valley",
            "unit": "per lb",
            "weight": "1 lb",
            "thumbnail": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500",
            "images": [
                "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=800",
                "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=800"
            ],
            "is_organic": True,
            "is_featured": True,
            "is_on_sale": True,
            "stock_quantity": 150,
            "tags": ["organic", "fruit", "fresh", "healthy"],
            "nutrition_facts": {
                "servingSize": "1 medium (118g)",
                "calories": 105,
                "totalFat": "0.4g",
                "sodium": "1mg",
                "carbohydrates": "27g",
                "fiber": "3.1g",
                "sugars": "14g",
                "protein": "1.3g"
            }
        },
        {
            "name": "Fresh Spinach",
            "description": "Crisp, fresh organic spinach leaves. Rich in iron and vitamins, perfect for salads and cooking.",
            "short_description": "Fresh organic spinach leaves",
            "price": 3.49,
            "cost_price": 1.75,
            "sku": "PROD-SPN-001",
            "category_slug": "fresh-produce",
            "brand": "Green Fields",
            "unit": "per bunch",
            "weight": "10 oz",
            "thumbnail": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=500",
            "images": [
                "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=800"
            ],
            "is_organic": True,
            "is_featured": True,
            "stock_quantity": 80,
            "tags": ["organic", "vegetable", "leafy-greens", "healthy"],
            "nutrition_facts": {
                "servingSize": "1 cup (30g)",
                "calories": 7,
                "totalFat": "0.1g",
                "sodium": "24mg",
                "carbohydrates": "1.1g",
                "fiber": "0.7g",
                "protein": "0.9g"
            }
        },
        {
            "name": "Organic Avocados",
            "description": "Creamy, ripe avocados perfect for toast, guacamole, or salads. Packed with healthy fats.",
            "short_description": "Creamy organic avocados",
            "price": 4.99,
            "original_price": 5.99,
            "cost_price": 2.50,
            "sku": "PROD-AVO-001",
            "category_slug": "fresh-produce",
            "brand": "Organic Valley",
            "unit": "per piece",
            "weight": "each",
            "thumbnail": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=500",
            "images": [
                "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=800"
            ],
            "is_organic": True,
            "is_on_sale": True,
            "stock_quantity": 120,
            "tags": ["organic", "fruit", "healthy-fats", "superfood"],
            "nutrition_facts": {
                "servingSize": "1/2 avocado (68g)",
                "calories": 114,
                "totalFat": "10.5g",
                "sodium": "5mg",
                "carbohydrates": "6g",
                "fiber": "4.6g",
                "protein": "1.3g"
            }
        },
        
        # Dairy & Eggs
        {
            "name": "Free-Range Eggs",
            "description": "Farm-fresh free-range eggs from pasture-raised chickens. Rich in protein and nutrients.",
            "short_description": "Farm-fresh free-range eggs",
            "price": 5.99,
            "cost_price": 3.00,
            "sku": "PROD-EGG-001",
            "category_slug": "dairy-eggs",
            "brand": "Happy Hens Farm",
            "unit": "per dozen",
            "weight": "12 eggs",
            "thumbnail": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=500",
            "images": [
                "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=800"
            ],
            "is_featured": True,
            "stock_quantity": 200,
            "tags": ["free-range", "protein", "breakfast", "farm-fresh"],
            "nutrition_facts": {
                "servingSize": "1 large egg (50g)",
                "calories": 72,
                "totalFat": "5g",
                "cholesterol": "186mg",
                "sodium": "71mg",
                "protein": "6g"
            }
        },
        {
            "name": "Organic Whole Milk",
            "description": "Fresh organic whole milk from grass-fed cows. Creamy and delicious.",
            "short_description": "Fresh organic whole milk",
            "price": 4.99,
            "cost_price": 2.50,
            "sku": "PROD-MLK-001",
            "category_slug": "dairy-eggs",
            "brand": "Organic Valley",
            "unit": "per gallon",
            "weight": "1 gallon",
            "thumbnail": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500",
            "images": [
                "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800"
            ],
            "is_organic": True,
            "is_featured": True,
            "stock_quantity": 90,
            "tags": ["organic", "dairy", "whole-milk", "vitamin-d"],
            "nutrition_facts": {
                "servingSize": "1 cup (244g)",
                "calories": 149,
                "totalFat": "8g",
                "saturatedFat": "4.6g",
                "cholesterol": "24mg",
                "sodium": "105mg",
                "carbohydrates": "12g",
                "protein": "8g"
            }
        },
        {
            "name": "Greek Yogurt",
            "description": "Thick and creamy Greek yogurt. High in protein and perfect for breakfast or snacks.",
            "short_description": "Creamy Greek yogurt",
            "price": 6.49,
            "original_price": 7.99,
            "cost_price": 3.25,
            "sku": "PROD-YOG-001",
            "category_slug": "dairy-eggs",
            "brand": "Chobani",
            "unit": "per container",
            "weight": "32 oz",
            "thumbnail": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=500",
            "images": [
                "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800"
            ],
            "is_on_sale": True,
            "stock_quantity": 110,
            "tags": ["protein", "probiotic", "breakfast", "healthy"],
            "nutrition_facts": {
                "servingSize": "1 cup (227g)",
                "calories": 100,
                "totalFat": "0g",
                "cholesterol": "10mg",
                "sodium": "65mg",
                "carbohydrates": "6g",
                "sugars": "4g",
                "protein": "17g"
            }
        },
        
        # Meat & Seafood
        {
            "name": "Wild-Caught Salmon",
            "description": "Premium wild-caught Atlantic salmon fillets. Rich in omega-3 fatty acids.",
            "short_description": "Wild-caught salmon fillets",
            "price": 18.99,
            "original_price": 22.99,
            "cost_price": 10.00,
            "sku": "PROD-SAL-001",
            "category_slug": "meat-seafood",
            "brand": "Ocean's Best",
            "unit": "per lb",
            "weight": "1 lb",
            "thumbnail": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500",
            "images": [
                "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800"
            ],
            "is_featured": True,
            "is_on_sale": True,
            "stock_quantity": 45,
            "tags": ["seafood", "omega-3", "protein", "wild-caught"],
            "nutrition_facts": {
                "servingSize": "3 oz (85g)",
                "calories": 177,
                "totalFat": "11g",
                "cholesterol": "55mg",
                "sodium": "50mg",
                "protein": "17g"
            }
        },
        {
            "name": "Organic Chicken Breast",
            "description": "Boneless, skinless organic chicken breast. Perfect for grilling or baking.",
            "short_description": "Organic chicken breast",
            "price": 9.99,
            "cost_price": 5.00,
            "sku": "PROD-CHK-001",
            "category_slug": "meat-seafood",
            "brand": "Organic Prairie",
            "unit": "per lb",
            "weight": "1 lb",
            "thumbnail": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500",
            "images": [
                "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=800"
            ],
            "is_organic": True,
            "stock_quantity": 70,
            "tags": ["organic", "protein", "chicken", "lean"],
            "nutrition_facts": {
                "servingSize": "4 oz (112g)",
                "calories": 165,
                "totalFat": "3.6g",
                "cholesterol": "85mg",
                "sodium": "74mg",
                "protein": "31g"
            }
        },
        
        # Bakery
        {
            "name": "Artisan Sourdough Bread",
            "description": "Handcrafted sourdough bread with a crispy crust and soft interior. Baked fresh daily.",
            "short_description": "Fresh artisan sourdough",
            "price": 4.49,
            "cost_price": 2.00,
            "sku": "PROD-BRD-001",
            "category_slug": "bakery",
            "brand": "Local Bakery",
            "unit": "per loaf",
            "weight": "1 loaf",
            "thumbnail": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=500",
            "images": [
                "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=800"
            ],
            "is_featured": True,
            "stock_quantity": 60,
            "tags": ["bread", "artisan", "fresh-baked", "sourdough"],
            "ingredients": "Organic wheat flour, water, salt, sourdough starter"
        },
        {
            "name": "Chocolate Croissants",
            "description": "Buttery, flaky croissants filled with rich chocolate. A perfect breakfast treat.",
            "short_description": "Buttery chocolate croissants",
            "price": 5.99,
            "cost_price": 2.50,
            "sku": "PROD-CRS-001",
            "category_slug": "bakery",
            "brand": "French Patisserie",
            "unit": "per pack",
            "weight": "4 pack",
            "thumbnail": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=500",
            "images": [
                "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800"
            ],
            "stock_quantity": 40,
            "tags": ["pastry", "chocolate", "breakfast", "french"],
            "allergens": ["wheat", "dairy", "eggs"]
        },
        
        # Beverages
        {
            "name": "Cold-Pressed Orange Juice",
            "description": "100% pure cold-pressed orange juice. No added sugars or preservatives.",
            "short_description": "Fresh cold-pressed OJ",
            "price": 6.99,
            "cost_price": 3.50,
            "sku": "PROD-JUC-001",
            "category_slug": "beverages",
            "brand": "Fresh Press",
            "unit": "per bottle",
            "weight": "64 oz",
            "thumbnail": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=500",
            "images": [
                "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=800"
            ],
            "is_featured": True,
            "stock_quantity": 85,
            "tags": ["juice", "vitamin-c", "fresh", "no-sugar-added"],
            "nutrition_facts": {
                "servingSize": "8 fl oz (240ml)",
                "calories": 110,
                "totalFat": "0g",
                "sodium": "0mg",
                "carbohydrates": "26g",
                "sugars": "22g",
                "protein": "2g",
                "vitaminC": "100% DV"
            }
        },
        {
            "name": "Organic Green Tea",
            "description": "Premium organic green tea bags. Rich in antioxidants and naturally energizing.",
            "short_description": "Organic green tea",
            "price": 7.99,
            "original_price": 9.99,
            "cost_price": 4.00,
            "sku": "PROD-TEA-001",
            "category_slug": "beverages",
            "brand": "Zen Leaves",
            "unit": "per box",
            "weight": "20 bags",
            "thumbnail": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500",
            "images": [
                "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800"
            ],
            "is_organic": True,
            "is_on_sale": True,
            "stock_quantity": 130,
            "tags": ["tea", "organic", "antioxidants", "healthy"]
        },
        
        # Pantry Staples
        {
            "name": "Organic Quinoa",
            "description": "Premium organic quinoa. A complete protein and versatile grain for salads and sides.",
            "short_description": "Organic quinoa grain",
            "price": 8.99,
            "cost_price": 4.50,
            "sku": "PROD-QUA-001",
            "category_slug": "pantry-staples",
            "brand": "Ancient Harvest",
            "unit": "per bag",
            "weight": "2 lb",
            "thumbnail": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500",
            "images": [
                "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800"
            ],
            "is_organic": True,
            "stock_quantity": 95,
            "tags": ["grain", "protein", "gluten-free", "organic"],
            "nutrition_facts": {
                "servingSize": "1/4 cup dry (45g)",
                "calories": 160,
                "totalFat": "2.5g",
                "sodium": "0mg",
                "carbohydrates": "29g",
                "fiber": "3g",
                "protein": "6g"
            }
        },
        {
            "name": "Extra Virgin Olive Oil",
            "description": "Premium cold-pressed extra virgin olive oil. Perfect for cooking and dressings.",
            "short_description": "Premium olive oil",
            "price": 12.99,
            "cost_price": 6.50,
            "sku": "PROD-OIL-001",
            "category_slug": "pantry-staples",
            "brand": "Mediterranean Gold",
            "unit": "per bottle",
            "weight": "750 ml",
            "thumbnail": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500",
            "images": [
                "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800"
            ],
            "is_featured": True,
            "stock_quantity": 75,
            "tags": ["oil", "healthy-fats", "cooking", "mediterranean"]
        },
        
        # Snacks & Sweets
        {
            "name": "Dark Chocolate Bar",
            "description": "70% cacao dark chocolate bar. Rich, smooth, and indulgent.",
            "short_description": "Premium dark chocolate",
            "price": 3.99,
            "cost_price": 1.50,
            "sku": "PROD-CHO-001",
            "category_slug": "snacks-sweets",
            "brand": "Lindt",
            "unit": "per bar",
            "weight": "100g",
            "thumbnail": "https://images.unsplash.com/photo-1511381939415-e44015466834?w=500",
            "images": [
                "https://images.unsplash.com/photo-1511381939415-e44015466834?w=800"
            ],
            "stock_quantity": 160,
            "tags": ["chocolate", "dark-chocolate", "treat", "antioxidants"],
            "allergens": ["milk", "soy"]
        },
        {
            "name": "Mixed Nuts",
            "description": "Premium roasted and salted mixed nuts. A healthy and satisfying snack.",
            "short_description": "Roasted mixed nuts",
            "price": 9.99,
            "original_price": 11.99,
            "cost_price": 5.00,
            "sku": "PROD-NUT-001",
            "category_slug": "snacks-sweets",
            "brand": "Nature's Best",
            "unit": "per container",
            "weight": "16 oz",
            "thumbnail": "https://images.unsplash.com/photo-1599599810694-b5f3a1a9e729?w=500",
            "images": [
                "https://images.unsplash.com/photo-1599599810694-b5f3a1a9e729?w=800"
            ],
            "is_on_sale": True,
            "stock_quantity": 105,
            "tags": ["nuts", "protein", "healthy-snack", "roasted"],
            "allergens": ["tree-nuts", "peanuts"]
        },
        
        # Frozen Foods
        {
            "name": "Frozen Berry Mix",
            "description": "Premium frozen berry blend with strawberries, blueberries, and raspberries.",
            "short_description": "Mixed frozen berries",
            "price": 7.99,
            "cost_price": 4.00,
            "sku": "PROD-BER-001",
            "category_slug": "frozen-foods",
            "brand": "Arctic Harvest",
            "unit": "per bag",
            "weight": "32 oz",
            "thumbnail": "https://images.unsplash.com/photo-1588450862596-8e8c4e4d6c5d?w=500",
            "images": [
                "https://images.unsplash.com/photo-1588450862596-8e8c4e4d6c5d?w=800"
            ],
            "stock_quantity": 90,
            "tags": ["frozen", "berries", "smoothies", "antioxidants"]
        },
        {
            "name": "Frozen Pizza",
            "description": "Gourmet frozen pizza with fresh mozzarella and basil. Ready in minutes.",
            "short_description": "Gourmet frozen pizza",
            "price": 8.99,
            "cost_price": 4.50,
            "sku": "PROD-PIZ-001",
            "category_slug": "frozen-foods",
            "brand": "DiGiorno",
            "unit": "per pizza",
            "weight": "27.5 oz",
            "thumbnail": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500",
            "images": [
                "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"
            ],
            "stock_quantity": 70,
            "tags": ["frozen", "pizza", "quick-meal", "italian"],
            "allergens": ["wheat", "dairy"]
        }
    ]
    
    for prod_data in products_data:
        # Get category ID
        category_slug = prod_data.pop("category_slug")
        category_id = category_map.get(category_slug)
        
        if not category_id:
            print(f"Warning: Category '{category_slug}' not found, skipping product '{prod_data['name']}'")
            continue
        
        # Check if product already exists
        existing = db.query(Product).filter(Product.sku == prod_data["sku"]).first()
        if existing:
            print(f"Product '{prod_data['name']}' already exists, skipping...")
            continue
        
        # Create product
        product = Product(
            id=str(uuid.uuid4()),
            slug=create_slug(prod_data["name"]),
            category_id=category_id,
            meta_title=prod_data.get("name"),
            meta_description=prod_data.get("short_description"),
            **prod_data
        )
        
        db.add(product)
        print(f"Created product: {prod_data['name']} - ${prod_data['price']}")
    
    db.commit()


def main():
    """Main seed function"""
    print("=" * 60)
    print("Starting database seed...")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Seed categories first
        print("\n📦 Seeding categories...")
        category_map = seed_categories(db)
        print(f"✅ Categories seeded successfully! ({len(category_map)} categories)")
        
        # Seed products
        print("\n🛒 Seeding products...")
        seed_products(db, category_map)
        print("✅ Products seeded successfully!")
        
        # Summary
        total_categories = db.query(Category).count()
        total_products = db.query(Product).count()
        
        print("\n" + "=" * 60)
        print("🎉 SEED COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Categories: {total_categories}")
        print(f"📊 Total Products: {total_products}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
