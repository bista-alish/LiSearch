"""
Liquor Store Database Seeder

"""

import os
from datetime import datetime, timedelta
import random
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def clear_all_data():
    """Clear all data from tables (idempotent)"""
    print("Clearing existing data...")
    tables = ['sales_line_items', 'sales_transactions', 'inventory', 'products', 'categories']
    for table in tables:
        supabase.table(table).delete().neq('id', 0).execute()
    print("✓ Data cleared")


def seed_categories():
    """Seed product categories"""
    print("Seeding categories...")
    categories = [
        {"name": "Wine", "description": "Red, white, rosé, and sparkling wines"},
        {"name": "Beer", "description": "Craft beers, lagers, ales, and imports"},
        {"name": "Spirits", "description": "Whiskey, vodka, rum, gin, and tequila"},
        {"name": "Liqueurs", "description": "Flavored spirits and cordials"},
        {"name": "Ready-to-Drink", "description": "Pre-mixed cocktails and hard seltzers"}
    ]
    
    result = supabase.table('categories').insert(categories).execute()
    print(f"✓ Seeded {len(result.data)} categories")
    return {cat['name']: cat['id'] for cat in result.data}


def seed_products(category_ids):
    """Seed product catalog with realistic liquor store items"""
    print("Seeding products...")
    
    products = [
        # Wines
        {"sku": "WIN-CAB-001", "upc": "012345678901", "name": "Château Margaux", "brand": "Château Margaux", 
         "category_id": category_ids["Wine"], "subcategory": "Red Wine - Bordeaux", "size": "750ml", "abv": 13.5,
         "description": "Full-bodied Bordeaux with notes of dark cherry, cedar, and tobacco. Smooth tannins with a long finish.",
         "cost_price": 45.00, "retail_price": 89.99, "status": "active"},
        
        {"sku": "WIN-CHARD-002", "upc": "012345678902", "name": "Kendall-Jackson Chardonnay", "brand": "Kendall-Jackson",
         "category_id": category_ids["Wine"], "subcategory": "White Wine - Chardonnay", "size": "750ml", "abv": 13.5,
           "description": "Rich and creamy Chardonnay with tropical fruit flavors, vanilla, and butter notes.",
         "cost_price": 12.00, "retail_price": 24.99, "status": "active"},
        
        {"sku": "WIN-PINOT-003", "upc": "012345678903", "name": "Meiomi Pinot Noir", "brand": "Meiomi",
         "category_id": category_ids["Wine"], "subcategory": "Red Wine - Pinot Noir", "size": "750ml", "abv": 13.8,
           "description": "Silky Pinot Noir with bright cherry, strawberry, and subtle oak. Elegant and food-friendly.",
         "cost_price": 13.50, "retail_price": 26.99, "status": "active"},
        
        {"sku": "WIN-SAUV-004", "upc": "012345678904", "name": "Kim Crawford Sauvignon Blanc", "brand": "Kim Crawford",
         "category_id": category_ids["Wine"], "subcategory": "White Wine - Sauvignon Blanc", "size": "750ml", "abv": 13.0,
          "description": "Crisp and refreshing with zesty citrus, passion fruit, and herbaceous notes.",
         "cost_price": 10.00, "retail_price": 19.99, "status": "active"},
        
        {"sku": "WIN-PROS-005", "upc": "012345678905", "name": "La Marca Prosecco", "brand": "La Marca",
         "category_id": category_ids["Wine"], "subcategory": "Sparkling Wine", "size": "750ml", "abv": 11.0,
          "description": "Light and bubbly Italian Prosecco with notes of green apple, pear, and white peach.",
         "cost_price": 9.00, "retail_price": 17.99, "status": "active"},
        
        # Beers
        {"sku": "BEER-IPA-101", "upc": "112345678901", "name": "Sierra Nevada Pale Ale", "brand": "Sierra Nevada",
         "category_id": category_ids["Beer"], "subcategory": "IPA", "size": "6-pack 12oz", "abv": 5.6,
          "description": "Classic American pale ale with piney, citrusy hops and balanced malt backbone.",
         "cost_price": 7.50, "retail_price": 12.99, "status": "active"},
        
        {"sku": "BEER-LAG-102", "upc": "112345678902", "name": "Stella Artois", "brand": "Stella Artois",
         "category_id": category_ids["Beer"], "subcategory": "Lager", "size": "6-pack 11.2oz", "abv": 5.0,
          "description": "Crisp Belgian lager with subtle malt sweetness and clean finish.",
         "cost_price": 6.50, "retail_price": 11.99, "status": "active"},
        
        {"sku": "BEER-STOUT-103", "upc": "112345678903", "name": "Guinness Draught", "brand": "Guinness",
         "category_id": category_ids["Beer"], "subcategory": "Stout", "size": "4-pack 14.9oz", "abv": 4.2,
          "description": "Iconic Irish stout with roasted barley, chocolate notes, and creamy texture.",
         "cost_price": 8.00, "retail_price": 13.99, "status": "active"},
        
        {"sku": "BEER-WHEAT-104", "upc": "112345678904", "name": "Blue Moon Belgian White", "brand": "Blue Moon",
         "category_id": category_ids["Beer"], "subcategory": "Wheat Beer", "size": "6-pack 12oz", "abv": 5.4,
          "description": "Smooth wheat beer with orange peel and coriander. Light and refreshing citrus notes.",
         "cost_price": 6.00, "retail_price": 10.99, "status": "active"},
        
        {"sku": "BEER-CRAFT-105", "upc": "112345678905", "name": "Dogfish Head 60 Minute IPA", "brand": "Dogfish Head",
         "category_id": category_ids["Beer"], "subcategory": "IPA", "size": "6-pack 12oz", "abv": 6.0,
          "description": "Continuously hopped IPA with complex citrus, pine, and caramel flavors.",
         "cost_price": 8.50, "retail_price": 14.99, "status": "active"},
        
        # Spirits
        {"sku": "SPRT-WHIS-201", "upc": "212345678901", "name": "Jack Daniel's Old No. 7", "brand": "Jack Daniel's",
         "category_id": category_ids["Spirits"], "subcategory": "Tennessee Whiskey", "size": "750ml", "abv": 40.0,
          "description": "Classic Tennessee whiskey with smooth caramel, vanilla, and charcoal mellowing. Woody undertones.",
         "cost_price": 18.00, "retail_price": 32.99, "status": "active"},
        
        {"sku": "SPRT-VODK-202", "upc": "212345678902", "name": "Grey Goose Vodka", "brand": "Grey Goose",
         "category_id": category_ids["Spirits"], "subcategory": "Vodka", "size": "750ml", "abv": 40.0,
          "description": "Premium French vodka with silky smooth texture and subtle sweetness. Clean finish.",
         "cost_price": 22.00, "retail_price": 39.99, "status": "active"},
        
        {"sku": "SPRT-GIN-203", "upc": "212345678903", "name": "Tanqueray London Dry Gin", "brand": "Tanqueray",
         "category_id": category_ids["Spirits"], "subcategory": "Gin", "size": "750ml", "abv": 47.3,
          "description": "Juniper-forward London dry gin with citrus, angelica, and licorice notes. Perfect for martinis.",
         "cost_price": 16.00, "retail_price": 28.99, "status": "active"},
        
        {"sku": "SPRT-RUM-204", "upc": "212345678904", "name": "Bacardi Superior", "brand": "Bacardi",
         "category_id": category_ids["Spirits"], "subcategory": "White Rum", "size": "750ml", "abv": 40.0,
          "description": "Light and crisp white rum with subtle vanilla and almond. Ideal for mojitos and daiquiris.",
         "cost_price": 12.00, "retail_price": 21.99, "status": "active"},
        
        {"sku": "SPRT-TEQ-205", "upc": "212345678905", "name": "Patrón Silver", "brand": "Patrón",
         "category_id": category_ids["Spirits"], "subcategory": "Tequila", "size": "750ml", "abv": 40.0,
          "description": "Premium silver tequila with citrus, pepper, and agave flavors. Smooth and clean.",
         "cost_price": 32.00, "retail_price": 54.99, "status": "active"},
        
        {"sku": "SPRT-SCOT-206", "upc": "212345678906", "name": "Johnnie Walker Black Label", "brand": "Johnnie Walker",
         "category_id": category_ids["Spirits"], "subcategory": "Scotch Whisky", "size": "750ml", "abv": 40.0,
          "description": "Blended Scotch with smoky peat, dried fruit, and vanilla. Rich and complex with woody notes.",
         "cost_price": 24.00, "retail_price": 42.99, "status": "active"},
        
        # Liqueurs
        {"sku": "LIQ-BAIL-301", "upc": "312345678901", "name": "Baileys Irish Cream", "brand": "Baileys",
         "category_id": category_ids["Liqueurs"], "subcategory": "Cream Liqueur", "size": "750ml", "abv": 17.0,
          "description": "Creamy blend of Irish whiskey and cream with chocolate and vanilla flavors.",
         "cost_price": 16.00, "retail_price": 27.99, "status": "active"},
        
        {"sku": "LIQ-COIN-302", "upc": "312345678902", "name": "Cointreau", "brand": "Cointreau",
         "category_id": category_ids["Liqueurs"], "subcategory": "Orange Liqueur", "size": "750ml", "abv": 40.0,
          "description": "Premium triple sec with intense orange peel flavor. Essential for margaritas and cosmopolitans.",
         "cost_price": 20.00, "retail_price": 36.99, "status": "active"},
        
        # Ready-to-Drink
        {"sku": "RTD-CLAW-401", "upc": "412345678901", "name": "White Claw Black Cherry", "brand": "White Claw",
         "category_id": category_ids["Ready-to-Drink"], "subcategory": "Hard Seltzer", "size": "12-pack 12oz", "abv": 5.0,
          "description": "Light and refreshing hard seltzer with natural black cherry flavor. Low calorie and gluten-free.",
         "cost_price": 13.00, "retail_price": 19.99, "status": "active"},
        
        {"sku": "RTD-MARG-402", "upc": "412345678902", "name": "Cutwater Lime Margarita", "brand": "Cutwater",
         "category_id": category_ids["Ready-to-Drink"], "subcategory": "Canned Cocktail", "size": "4-pack 12oz", "abv": 12.5,
          "description": "Premium ready-to-drink margarita with real tequila, lime juice, and agave. Tangy and refreshing citrus profile.",
         "cost_price": 11.00, "retail_price": 17.99, "status": "active"},
    ]
    
    result = supabase.table('products').insert(products).execute()
    print(f"✓ Seeded {len(result.data)} products")
    return [p['id'] for p in result.data]


def seed_inventory(product_ids):
    """Seed inventory with realistic stock levels"""
    print("Seeding inventory...")
    
    inventory_items = []
    for product_id in product_ids:
        inventory_items.append({
            "product_id": product_id,
            "quantity_on_hand": random.randint(10, 150),
            "reorder_level": random.randint(10, 30),
            "reorder_quantity": random.choice([12, 24, 36, 48]),
            "last_restock_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    result = supabase.table('inventory').insert(inventory_items).execute()
    print(f"✓ Seeded {len(result.data)} inventory records")


def seed_sales(product_ids):
    """Seed realistic sales transactions over the past 30 days"""
    print("Seeding sales transactions...")
    
    transactions = []
    line_items = []
    
    # Generate 200 transactions over the past 30 days
    for i in range(200):
        transaction_date = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Create transaction
        num_items = random.randint(1, 5)
        selected_products = random.sample(product_ids, num_items)
        
        total_amount = 0
        temp_line_items = []
        
        for product_id in selected_products:
            # Get product price (we'll use avg retail price for simplicity in seed)
            quantity = random.randint(1, 3)
            unit_price = random.uniform(10.99, 54.99)
            line_total = quantity * unit_price
            total_amount += line_total
            
            temp_line_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
                "line_total": round(line_total, 2),
                "discount_amount": 0
            })
        
        transactions.append({
            "transaction_date": transaction_date.isoformat(),
            "total_amount": round(total_amount, 2),
            "payment_method": random.choice(["cash", "card", "digital_wallet"])
        })
        
        # Store temp line items with transaction index
        line_items.append((i, temp_line_items))
    
    # Insert transactions
    result = supabase.table('sales_transactions').insert(transactions).execute()
    print(f"✓ Seeded {len(result.data)} sales transactions")
    
    # Insert line items with actual transaction IDs
    all_line_items = []
    for idx, (original_idx, items) in enumerate(line_items):
        transaction_id = result.data[original_idx]['id']
        for item in items:
            item['transaction_id'] = transaction_id
            all_line_items.append(item)
    
    result = supabase.table('sales_line_items').insert(all_line_items).execute()
    print(f"✓ Seeded {len(result.data)} sales line items")


def main():
    """Main seeding function"""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)
    
    # Clear existing data
    clear_all_data()
    
    # Seed data in order
    category_ids = seed_categories()
    product_ids = seed_products(category_ids)
    seed_inventory(product_ids)
    seed_sales(product_ids)
    
    print("=" * 50)
    print("✓ Database seeding completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()