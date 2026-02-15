"""
Seed script to populate PRODUCTION database via API
Usage: python scripts/seed_production_api.py
"""
import requests
import json
from typing import Dict, Optional

# Production API URL
API_BASE_URL = "https://fastapi.kevinlinportfolio.com/api/v1"

# Admin credentials
print("Note: Try the password you used when creating the admin account")
print("Common passwords: @Kevinlin1234, admin, Kevinlin1234!")
ADMIN_EMAIL = input("Enter admin email (or press Enter for lin.kevin.1923@gmail.com): ").strip() or "lin.kevin.1923@gmail.com"
ADMIN_PASSWORD = input("Enter admin password: ")


def login() -> Optional[str]:
    """Login and get access token"""
    print("🔐 Logging in as admin...")
    
    response = requests.post(
        f"{API_BASE_URL}/auth/token",
        data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def get_headers(token: str) -> Dict[str, str]:
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def create_category(token: str, category_data: dict) -> Optional[str]:
    """Create a category and return its ID"""
    headers = get_headers(token)
    
    response = requests.post(
        f"{API_BASE_URL}/categories/",
        headers=headers,
        json=category_data
    )
    
    if response.status_code == 200:
        category = response.json()
        print(f"✅ Created category: {category_data['name']}")
        return category["id"]
    elif response.status_code == 400 and "already exists" in response.text:
        # Category exists, get it
        response = requests.get(f"{API_BASE_URL}/categories/")
        categories = response.json().get("items", [])
        for cat in categories:
            if cat["slug"] == category_data["slug"]:
                print(f"⏭️  Category '{category_data['name']}' already exists")
                return cat["id"]
    else:
        print(f"⚠️  Failed to create category {category_data['name']}: {response.status_code}")
        print(response.text)
    
    return None


def create_product(token: str, product_data: dict) -> bool:
    """Create a product"""
    headers = get_headers(token)
    
    response = requests.post(
        f"{API_BASE_URL}/products/",
        headers=headers,
        json=product_data
    )
    
    if response.status_code == 200:
        product = response.json()
        print(f"✅ Created product: {product_data['name']} - ${product_data['price']}")
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"⏭️  Product '{product_data['name']}' already exists")
        return False
    else:
        print(f"⚠️  Failed to create product {product_data['name']}: {response.status_code}")
        print(response.text[:200])
        return False


def main():
    """Main seed function"""
    print("=" * 60)
    print("🚀 SEEDING PRODUCTION DATABASE VIA API")
    print("=" * 60)
    print(f"API: {API_BASE_URL}")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Categories data
    categories_data = [
        {"name": "Fresh Produce", "slug": "fresh-produce", "description": "Fresh fruits and vegetables", "icon": "🥬", "is_featured": True, "sort_order": 1},
        {"name": "Dairy & Eggs", "slug": "dairy-eggs", "description": "Milk, cheese, yogurt, and eggs", "icon": "🥛", "is_featured": True, "sort_order": 2},
        {"name": "Meat & Seafood", "slug": "meat-seafood", "description": "Fresh and frozen meat and seafood", "icon": "🥩", "is_featured": True, "sort_order": 3},
        {"name": "Bakery", "slug": "bakery", "description": "Fresh bread, pastries, and baked goods", "icon": "🍞", "is_featured": True, "sort_order": 4},
        {"name": "Beverages", "slug": "beverages", "description": "Drinks, juices, and refreshments", "icon": "🥤", "is_featured": True, "sort_order": 5},
        {"name": "Pantry Staples", "slug": "pantry-staples", "description": "Pasta, rice, canned goods, and essentials", "icon": "🥫", "is_featured": False, "sort_order": 6},
        {"name": "Snacks & Sweets", "slug": "snacks-sweets", "description": "Chips, cookies, candy, and treats", "icon": "🍪", "is_featured": False, "sort_order": 7},
        {"name": "Frozen Foods", "slug": "frozen-foods", "description": "Frozen meals, vegetables, and desserts", "icon": "🧊", "is_featured": False, "sort_order": 8},
    ]
    
    # Create categories
    print("\n📦 Creating categories...")
    category_map = {}
    for cat_data in categories_data:
        cat_id = create_category(token, cat_data)
        if cat_id:
            category_map[cat_data["slug"]] = cat_id
    
    print(f"\n✅ Categories ready: {len(category_map)}")
    
    # Products data
    products_data = [
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
            "images": ["https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=800"],
            "is_organic": True,
            "is_featured": True,
            "is_on_sale": True,
            "stock_quantity": 150,
            "tags": ["organic", "fruit", "fresh", "healthy"]
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
            "images": ["https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=800"],
            "is_organic": True,
            "is_featured": True,
            "stock_quantity": 80,
            "tags": ["organic", "vegetable", "leafy-greens", "healthy"]
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
            "images": ["https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=800"],
            "is_organic": True,
            "is_on_sale": True,
            "stock_quantity": 120,
            "tags": ["organic", "fruit", "healthy-fats", "superfood"]
        },
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
            "images": ["https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=800"],
            "is_featured": True,
            "stock_quantity": 200,
            "tags": ["free-range", "protein", "breakfast", "farm-fresh"]
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
            "images": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800"],
            "is_organic": True,
            "is_featured": True,
            "stock_quantity": 90,
            "tags": ["organic", "dairy", "whole-milk", "vitamin-d"]
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
            "images": ["https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800"],
            "is_on_sale": True,
            "stock_quantity": 110,
            "tags": ["protein", "probiotic", "breakfast", "healthy"]
        },
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
            "images": ["https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=800"],
            "is_featured": True,
            "is_on_sale": True,
            "stock_quantity": 45,
            "tags": ["seafood", "omega-3", "protein", "wild-caught"]
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
            "images": ["https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=800"],
            "is_organic": True,
            "stock_quantity": 70,
            "tags": ["organic", "protein", "chicken", "lean"]
        },
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
            "images": ["https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=800"],
            "is_featured": True,
            "stock_quantity": 60,
            "tags": ["bread", "artisan", "fresh-baked", "sourdough"]
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
            "images": ["https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=800"],
            "stock_quantity": 40,
            "tags": ["pastry", "chocolate", "breakfast", "french"]
        },
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
            "images": ["https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=800"],
            "is_featured": True,
            "stock_quantity": 85,
            "tags": ["juice", "vitamin-c", "fresh", "no-sugar-added"]
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
            "images": ["https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800"],
            "is_organic": True,
            "is_on_sale": True,
            "stock_quantity": 130,
            "tags": ["tea", "organic", "antioxidants", "healthy"]
        },
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
            "images": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800"],
            "is_organic": True,
            "stock_quantity": 95,
            "tags": ["grain", "protein", "gluten-free", "organic"]
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
            "images": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800"],
            "is_featured": True,
            "stock_quantity": 75,
            "tags": ["oil", "healthy-fats", "cooking", "mediterranean"]
        },
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
            "images": ["https://images.unsplash.com/photo-1511381939415-e44015466834?w=800"],
            "stock_quantity": 160,
            "tags": ["chocolate", "dark-chocolate", "treat", "antioxidants"]
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
            "images": ["https://images.unsplash.com/photo-1599599810694-b5f3a1a9e729?w=800"],
            "is_on_sale": True,
            "stock_quantity": 105,
            "tags": ["nuts", "protein", "healthy-snack", "roasted"]
        },
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
            "images": ["https://images.unsplash.com/photo-1588450862596-8e8c4e4d6c5d?w=800"],
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
            "images": ["https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"],
            "stock_quantity": 70,
            "tags": ["frozen", "pizza", "quick-meal", "italian"]
        }
    ]
    
    # Create products
    print("\n🛒 Creating products...")
    created = 0
    skipped = 0
    
    for prod_data in products_data:
        category_slug = prod_data.pop("category_slug")
        category_id = category_map.get(category_slug)
        
        if not category_id:
            print(f"⚠️  Category '{category_slug}' not found for product '{prod_data['name']}'")
            skipped += 1
            continue
        
        prod_data["category_id"] = category_id
        
        if create_product(token, prod_data):
            created += 1
        else:
            skipped += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 PRODUCTION SEED COMPLETE!")
    print("=" * 60)
    print(f"✨ New Products Created: {created}")
    print(f"⏭️  Products Skipped: {skipped}")
    print("=" * 60)
    print(f"\n🌐 View products: {API_BASE_URL}/products/")
    print("=" * 60)


if __name__ == "__main__":
    main()
