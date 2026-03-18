#!/usr/bin/env python3
"""
Comprehensive data management script for PC Shop.
Handles all data operations: adding products, clearing data, and managing categories.
"""

import os
import sys
import django
import random
from decimal import Decimal

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pc_shop.settings')
django.setup()

from products.models import Product, Category, Brand
from orders.models import Order, OrderItem
from payments.models import Payment


def create_brands():
    """Create brands for PC components"""
    brands_data = [
        {'name': 'Intel', 'description': 'Leading processor manufacturer'},
        {'name': 'AMD', 'description': 'Advanced Micro Devices - CPUs and GPUs'},
        {'name': 'ASUS', 'description': 'Computer hardware and electronics'},
        {'name': 'MSI', 'description': 'Micro-Star International - Gaming hardware'},
        {'name': 'Gigabyte', 'description': 'Manufacturer of motherboards and graphics cards'},
        {'name': 'Corsair', 'description': 'Gaming peripherals and components'},
        {'name': 'G.SKILL', 'description': 'Memory and storage solutions'},
        {'name': 'NVIDIA', 'description': 'Graphics processing units'},
        {'name': 'Samsung', 'description': 'Storage and memory solutions'},
        {'name': 'Seagate', 'description': 'Data storage solutions'},
        {'name': 'EVGA', 'description': 'Graphics cards and power supplies'},
        {'name': 'Fractal Design', 'description': 'PC cases and cooling'},
        {'name': 'Lian Li', 'description': 'Premium PC cases'},
        {'name': 'Noctua', 'description': 'Premium cooling solutions'},
    ]
    
    created_brands = {}
    print("Creating/Finding Brands...")
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'description': brand_data['description']}
        )
        created_brands[brand_data['name']] = brand
        print(f"{'Created' if created else 'Found'} brand: {brand.name}")
    
    return created_brands


def create_categories():
    """Create product categories for PC components"""
    # Use the exact category names that the customization view expects
    categories_data = [
        {'name': 'CPU', 'description': 'Central Processing Units'},
        {'name': 'Motherboard', 'description': 'Main circuit boards'},
        {'name': 'RAM', 'description': 'System memory modules'},
        {'name': 'GPU', 'description': 'Video graphics cards'},
        {'name': 'Storage', 'description': 'Hard drives and SSDs'},
        {'name': 'PSU', 'description': 'Power supply units'},
        {'name': 'Case', 'description': 'PC cases and enclosures'},
        {'name': 'Cooling', 'description': 'CPU coolers and case fans'},
        {'name': 'Optical Drives', 'description': 'DVD/Blu-ray drives'},
    ]
    
    created_categories = {}
    print("Creating/Finding Categories...")
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        created_categories[cat_data['name']] = category
        print(f"{'Created' if created else 'Found'} category: {category.name}")
    
    return created_categories


def add_custom_pc_products():
    """Add products needed for custom PC building"""
    
    # Create categories and brands first
    categories = create_categories()
    brands = create_brands()
    
    # PC Components data - using exact category names expected by customization view
    pc_products = [
        # CPUs
        {
            'name': 'Intel Core i9-13900K',
            'category': 'CPU',
            'price': Decimal('589.99'),
            'description': '24-core (8P+16E) processor with 32 threads, 3.0GHz base clock, 5.8GHz max boost. Socket LGA1700, 24 cores, 32 threads, 125W TDP',
            'stock': 20,
            'brand': 'Intel',
        },
        {
            'name': 'Intel Core i7-13700K',
            'category': 'CPU',
            'price': Decimal('409.99'),
            'description': '16-core (8P+8E) processor with 24 threads, 3.4GHz base clock, 5.4GHz max boost. Socket LGA1700, 16 cores, 24 threads, 125W TDP',
            'stock': 25,
            'brand': 'Intel',
        },
        {
            'name': 'Intel Core i5-13600K',
            'category': 'CPU',
            'price': Decimal('319.99'),
            'description': '14-core (6P+8E) processor with 20 threads, 3.5GHz base clock, 5.1GHz max boost. Socket LGA1700, 14 cores, 20 threads, 125W TDP',
            'stock': 30,
            'brand': 'Intel',
        },
        {
            'name': 'AMD Ryzen 9 7950X',
            'category': 'CPU',
            'price': Decimal('599.99'),
            'description': '16-core processor with 32 threads, 4.5GHz base clock, 5.7GHz max boost. Socket AM5, 16 cores, 32 threads, 170W TDP',
            'stock': 18,
            'brand': 'AMD',
        },
        {
            'name': 'AMD Ryzen 7 7700X',
            'category': 'CPU',
            'price': Decimal('349.99'),
            'description': '8-core processor with 16 threads, 4.5GHz base clock, 5.4GHz max boost. Socket AM5, 8 cores, 16 threads, 105W TDP',
            'stock': 30,
            'brand': 'AMD',
        },
        
        # Motherboards
        {
            'name': 'ASUS ROG STRIX Z790-E GAMING',
            'category': 'Motherboard',
            'price': Decimal('449.99'),
            'description': 'ATX motherboard with WiFi 6E, DDR5 support, PCIe 5.0. LGA1700, DDR5, PCIe 5.0, WiFi 6E, 2.5Gb Ethernet',
            'stock': 15,
            'brand': 'ASUS',
        },
        {
            'name': 'MSI MPG Z790 EDGE WIFI',
            'category': 'Motherboard',
            'price': Decimal('369.99'),
            'description': 'ATX motherboard with stylish silver design, WiFi 6E, DDR5 support. LGA1700, DDR5, PCIe 5.0, WiFi 6E',
            'stock': 18,
            'brand': 'MSI',
        },
        {
            'name': 'MSI MAG B650 TOMAHAWK WIFI',
            'category': 'Motherboard',
            'price': Decimal('229.99'),
            'description': 'ATX motherboard with WiFi 6, DDR5 support, PCIe 4.0. AM5, DDR5, PCIe 4.0, WiFi 6, Gigabit Ethernet',
            'stock': 20,
            'brand': 'MSI',
        },
        {
            'name': 'Gigabyte B650 AORUS ELITE AX',
            'category': 'Motherboard',
            'price': Decimal('199.99'),
            'description': 'ATX motherboard with solid performance for AMD. AM5, DDR5, PCIe 4.0, WiFi 6, Gigabit Ethernet',
            'stock': 22,
            'brand': 'Gigabyte',
        },
        
        # RAM
        {
            'name': 'Corsair Vengeance RGB Pro 32GB (2x16GB) DDR5-6000',
            'category': 'RAM',
            'price': Decimal('149.99'),
            'description': 'High-performance DDR5 memory kit with RGB lighting, 32GB total capacity. DDR5-6000, CL36, 1.35V, RGB, Dual Channel Kit',
            'stock': 35,
            'brand': 'Corsair',
        },
        {
            'name': 'Corsair Dominator Platinum RGB 64GB (2x32GB) DDR5-5600',
            'category': 'RAM',
            'price': Decimal('329.99'),
            'description': 'Premium DDR5 memory kit with advanced RGB lighting, 64GB total capacity. DDR5-5600, CL36, 1.25V, RGB, Dual Channel Kit',
            'stock': 15,
            'brand': 'Corsair',
        },
        {
            'name': 'G.SKILL Trident Z5 32GB (2x16GB) DDR5-6000',
            'category': 'RAM',
            'price': Decimal('139.99'),
            'description': 'High-speed DDR5 memory kit with sleek design, 32GB total capacity. DDR5-6000, CL36, 1.35V, Dual Channel Kit',
            'stock': 25,
            'brand': 'G.SKILL',
        },
        {
            'name': 'Corsair Vengeance LPX 32GB (2x16GB) DDR4-3200',
            'category': 'RAM',
            'price': Decimal('89.99'),
            'description': 'High-performance DDR4 memory kit, 32GB total capacity. DDR4-3200, CL16, 1.35V, Dual Channel Kit',
            'stock': 40,
            'brand': 'Corsair',
        },
        
        # GPUs
        {
            'name': 'ASUS ROG STRIX RTX 4090 Gaming OC',
            'category': 'GPU',
            'price': Decimal('1699.99'),
            'description': 'Top-tier graphics card for 4K gaming and content creation. 24GB GDDR6X, 2520 MHz boost clock, Ray Tracing, DLSS 3',
            'stock': 8,
            'brand': 'ASUS',
        },
        {
            'name': 'MSI RTX 4070 Ti SUPRIM X',
            'category': 'GPU',
            'price': Decimal('899.99'),
            'description': 'Excellent 1440p gaming performance with premium cooling. 12GB GDDR6X, 2610 MHz boost clock, Ray Tracing, DLSS 3',
            'stock': 12,
            'brand': 'MSI',
        },
        {
            'name': 'NVIDIA GeForce RTX 4070 Ti',
            'category': 'GPU',
            'price': Decimal('799.99'),
            'description': 'High-performance graphics card for 1440p gaming. 12GB GDDR6X, 2610 MHz boost clock, Ray Tracing, DLSS 3',
            'stock': 15,
            'brand': 'NVIDIA',
        },
        {
            'name': 'AMD Radeon RX 7900 XTX',
            'category': 'GPU',
            'price': Decimal('999.99'),
            'description': 'AMD flagship GPU for high-end gaming. 24GB GDDR6, 2500 MHz boost clock, Ray Tracing, FSR 3',
            'stock': 10,
            'brand': 'AMD',
        },
        {
            'name': 'AMD Radeon RX 7800 XT',
            'category': 'GPU',
            'price': Decimal('499.99'),
            'description': 'Excellent 1440p gaming performance with 16GB VRAM. 16GB GDDR6, 2430 MHz boost clock, Ray Tracing, FSR 3',
            'stock': 18,
            'brand': 'AMD',
        },
        
        # Storage
        {
            'name': 'Samsung 990 PRO 2TB NVMe SSD',
            'category': 'Storage',
            'price': Decimal('179.99'),
            'description': 'High-speed NVMe SSD with PCIe 4.0 interface, 2TB capacity. PCIe 4.0, 7450 MB/s read, 6900 MB/s write',
            'stock': 25,
            'brand': 'Samsung',
        },
        {
            'name': 'Samsung 980 PRO 1TB NVMe SSD',
            'category': 'Storage',
            'price': Decimal('79.99'),
            'description': 'High-speed NVMe SSD with PCIe 4.0 interface, 1TB capacity. PCIe 4.0, 7000 MB/s read, 5000 MB/s write',
            'stock': 35,
            'brand': 'Samsung',
        },
        {
            'name': 'Seagate Barracuda 2TB HDD',
            'category': 'Storage',
            'price': Decimal('54.99'),
            'description': 'Reliable 7200 RPM hard drive for mass storage. 2TB, 7200 RPM, SATA 6Gb/s, 256MB cache',
            'stock': 50,
            'brand': 'Seagate',
        },
        {
            'name': 'Samsung 970 EVO Plus 1TB NVMe SSD',
            'category': 'Storage',
            'price': Decimal('59.99'),
            'description': 'Reliable NVMe SSD with good performance. 1TB, PCIe 3.0, 3500 MB/s read, 3300 MB/s write',
            'stock': 40,
            'brand': 'Samsung',
        },
        
        # PSUs
        {
            'name': 'Corsair RM850x 850W 80+ Gold',
            'category': 'PSU',
            'price': Decimal('149.99'),
            'description': 'Fully modular power supply with 80+ Gold efficiency. 850W, 80+ Gold, Fully Modular, 10-year warranty',
            'stock': 22,
            'brand': 'Corsair',
        },
        {
            'name': 'Corsair HX1000i 1000W 80+ Platinum',
            'category': 'PSU',
            'price': Decimal('259.99'),
            'description': 'Premium fully modular PSU with digital monitoring. 1000W, 80+ Platinum, Fully Modular, 10-year warranty',
            'stock': 15,
            'brand': 'Corsair',
        },
        {
            'name': 'EVGA SuperNOVA 750 G6 750W 80+ Gold',
            'category': 'PSU',
            'price': Decimal('119.99'),
            'description': 'Compact fully modular PSU with excellent efficiency. 750W, 80+ Gold, Fully Modular, 10-year warranty',
            'stock': 28,
            'brand': 'EVGA',
        },
        
        # Cases
        {
            'name': 'Corsair 4000D Airflow',
            'category': 'Case',
            'price': Decimal('104.99'),
            'description': 'High airflow mid-tower case with excellent build quality. Mid-tower, High airflow, USB-C, Tempered glass',
            'stock': 20,
            'brand': 'Corsair',
        },
        {
            'name': 'Lian Li O11 Dynamic EVO',
            'category': 'Case',
            'price': Decimal('169.99'),
            'description': 'Premium showcase chassis with dual-chamber design. Mid-tower, Dual chamber, Tempered glass, 10 fan mounts',
            'stock': 12,
            'brand': 'Lian Li',
        },
        {
            'name': 'Fractal Design Define 7 Compact',
            'category': 'Case',
            'price': Decimal('109.99'),
            'description': 'Silent mid-tower case with excellent build quality. Mid-tower, Sound dampening, USB-C, Tempered glass',
            'stock': 15,
            'brand': 'Fractal Design',
        },
        {
            'name': 'Lian Li PC-O11 Dynamic',
            'category': 'Case',
            'price': Decimal('139.99'),
            'description': 'Popular dual-chamber case with excellent airflow. Mid-tower, Dual chamber, Tempered glass, 9 fan mounts',
            'stock': 18,
            'brand': 'Lian Li',
        },
        
        # Cooling
        {
            'name': 'Corsair H150i Elite LCD 360mm AIO',
            'category': 'Cooling',
            'price': Decimal('289.99'),
            'description': '360mm liquid CPU cooler with LCD screen and RGB lighting. 360mm radiator, LCD screen, RGB lighting, iCUE software',
            'stock': 12,
            'brand': 'Corsair',
        },
        {
            'name': 'Noctua NH-D15 CPU Cooler',
            'category': 'Cooling',
            'price': Decimal('109.99'),
            'description': 'Premium dual-tower air cooler with excellent performance. Dual tower, 2x 140mm fans, LGA1700/AM5 compatible',
            'stock': 20,
            'brand': 'Noctua',
        },
        {
            'name': 'Corsair iCUE H100i RGB PRO XT',
            'category': 'Cooling',
            'price': Decimal('119.99'),
            'description': '240mm liquid CPU cooler with RGB lighting. 240mm radiator, RGB lighting, iCUE software',
            'stock': 18,
            'brand': 'Corsair',
        },
        
        # Optical Drives
        {
            'name': 'ASUS DRW-24B1ST DVD Writer',
            'category': 'Optical Drives',
            'price': Decimal('19.99'),
            'description': 'Internal DVD/CD writer with SATA interface. DVD±R/RW, CD-R/RW, SATA, 24x write speed',
            'stock': 30,
            'brand': 'ASUS',
        },
    ]
    
    # Add products to database
    created_count = 0
    print("\nAdding Products...")
    for product_data in pc_products:
        category = categories[product_data['category']]
        brand = brands[product_data['brand']]
        
        # Check if product already exists
        if Product.objects.filter(name=product_data['name']).exists():
            print(f"Product already exists: {product_data['name']}")
            continue
        
        # Create product (image field is required but we'll use a placeholder)
        try:
            product = Product.objects.create(
                name=product_data['name'],
                category=category,
                brand=brand,
                price=product_data['price'],
                description=product_data['description'],
                stock=product_data['stock'],
                image='product_images/placeholder.jpg',  # Placeholder image
                is_prebuilt=False,
            )
            created_count += 1
            print(f"Created product: {product.name} - ${product.price}")
        except Exception as e:
            print(f"Error creating product {product_data['name']}: {str(e)}")
    
    print(f"\nSummary: {created_count} new products added to the database.")
    return created_count


def clear_orders():
    """Clear all orders and related data"""
    print("Clearing database orders...")
    
    # Delete OrderItems first
    items_deleted = OrderItem.objects.all().delete()
    print(f"Deleted {items_deleted[0]} Order Items.")
    
    # Delete Payments
    try:
        payments_deleted = Payment.objects.all().delete()
        print(f"Deleted {payments_deleted[0]} Payments.")
    except Exception as e:
        print(f"Error clearing payments: {e}")

    # Delete Orders
    orders_deleted = Order.objects.all().delete()
    print(f"Deleted {orders_deleted[0]} Orders.")
    
    print("Success! All orders have been cleared.")


def clear_all_products():
    """Clear all products from database"""
    confirmation = input("Are you sure you want to delete ALL products? (yes/no): ")
    if confirmation.lower() == 'yes':
        products_deleted = Product.objects.all().delete()
        print(f"Deleted {products_deleted[0]} products.")
        print("Success! All products have been cleared.")
    else:
        print("Operation cancelled.")


def show_stats():
    """Show database statistics"""
    print("\n=== Database Statistics ===")
    print(f"Categories: {Category.objects.count()}")
    print(f"Brands: {Brand.objects.count()}")
    print(f"Products: {Product.objects.count()}")
    print(f"Orders: {Order.objects.count()}")
    
    print("\n=== Products by Category ===")
    for category in Category.objects.all():
        count = Product.objects.filter(category=category).count()
        print(f"{category.name}: {count} products")


def main():
    """Main menu for data management"""
    while True:
        print("\n" + "="*50)
        print("PC Shop Data Management")
        print("="*50)
        print("1. Add Custom PC Products")
        print("2. Clear Orders")
        print("3. Clear All Products")
        print("4. Show Database Stats")
        print("5. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\nAdding Custom PC Products...")
            count = add_custom_pc_products()
            print(f"✅ Operation completed! {count} products added.")
            
        elif choice == '2':
            confirmation = input("Are you sure you want to delete ALL orders? (yes/no): ")
            if confirmation.lower() == 'yes':
                clear_orders()
                print("✅ Orders cleared successfully!")
            else:
                print("Operation cancelled.")
                
        elif choice == '3':
            clear_all_products()
            
        elif choice == '4':
            show_stats()
            
        elif choice == '5':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)