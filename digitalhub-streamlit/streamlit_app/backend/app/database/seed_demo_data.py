"""
Demo marketplace seed.

Populates 10 electronics vendors with a 30-product catalog (VendorProduct —
what a vendor manages from My Products), plus a mirrored, dataset-linked
Product/Order/Customer history so every analytics page (Admin Dashboard,
Vendor Management, Vendor Details, Customer/Sales Analytics, Reports, and
the Vendor-side Dashboard/Inventory/Sales Analytics/Reports) has real data
to render immediately — no manual CSV upload required.

Idempotent: skipped entirely if any seed vendor already exists.
"""
import random
import uuid
from datetime import datetime, timedelta, timezone

from app.auth.security import hash_password
from app.database.session import SessionLocal
from app.models.customer import Customer
from app.models.dataset import Dataset, DatasetStatus
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User, UserRole, VendorStatus
from app.models.vendor_product import VendorProduct, VendorProductStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEED_MARKER_EMAIL = "contact@nexoraelectronics.in"

VENDORS = [
    {"business_name": "Nexora Electronics", "owner": "Aarav Shah", "city": "Bengaluru", "state": "Karnataka", "status": VendorStatus.ACTIVE, "commission": 10.0},
    {"business_name": "PulseTech Store", "owner": "Meera Kulkarni", "city": "Pune", "state": "Maharashtra", "status": VendorStatus.ACTIVE, "commission": 12.0},
    {"business_name": "ByteHub Gadgets", "owner": "Rohan Verma", "city": "Delhi", "state": "Delhi", "status": VendorStatus.ACTIVE, "commission": 9.5},
    {"business_name": "Circuit Bazaar", "owner": "Sanya Kapoor", "city": "Ahmedabad", "state": "Gujarat", "status": VendorStatus.ACTIVE, "commission": 11.0},
    {"business_name": "VoltEdge Electronics", "owner": "Kabir Malhotra", "city": "Chennai", "state": "Tamil Nadu", "status": VendorStatus.ACTIVE, "commission": 8.5},
    {"business_name": "TechNova Retail", "owner": "Ishita Reddy", "city": "Hyderabad", "state": "Telangana", "status": VendorStatus.ACTIVE, "commission": 13.0},
    {"business_name": "Quantum Gadgets Co.", "owner": "Vivaan Nair", "city": "Kochi", "state": "Kerala", "status": VendorStatus.ACTIVE, "commission": 10.5},
    {"business_name": "GadgetSphere", "owner": "Ananya Das", "city": "Kolkata", "state": "West Bengal", "status": VendorStatus.PENDING, "commission": 10.0},
    {"business_name": "SmartCore Electronics", "owner": "Farhan Sheikh", "city": "Jaipur", "state": "Rajasthan", "status": VendorStatus.PENDING, "commission": 10.0},
    {"business_name": "FutureTech Mart", "owner": "Devika Rao", "city": "Mumbai", "state": "Maharashtra", "status": VendorStatus.SUSPENDED, "commission": 14.0},
]

# 30 electronics products: (name, category, price, stock, brand)
PRODUCTS = [
    ("Pulse X12 5G Smartphone", "Smartphones", 24999, 42, "Pulse"),
    ("Nova Lite 128GB", "Smartphones", 15999, 65, "Nova"),
    ("Zenith Pro Max", "Smartphones", 54999, 18, "Zenith"),
    ("Orbit S 5G", "Smartphones", 19999, 8, "Orbit"),
    ("AeroBook 14 Ultraslim Laptop", "Laptops & Computers", 62999, 22, "Aero"),
    ("TitanForce Gaming Laptop", "Laptops & Computers", 98999, 12, "Titan"),
    ("CompactDesk Mini PC", "Laptops & Computers", 28999, 30, "CompactDesk"),
    ("ProNote 2-in-1 Convertible", "Laptops & Computers", 71999, 15, "ProNote"),
    ("SonicWave ANC Headphones", "Audio & Headphones", 6999, 80, "SonicWave"),
    ("BassPods True Wireless Earbuds", "Audio & Headphones", 3499, 120, "BassPods"),
    ("StageSound Bluetooth Speaker", "Audio & Headphones", 4999, 55, "StageSound"),
    ("ClarityMic USB Podcast Mic", "Audio & Headphones", 5499, 9, "Clarity"),
    ("PulseFit Smartwatch", "Wearables", 8999, 47, "PulseFit"),
    ("TrackBand Fitness Tracker", "Wearables", 2999, 90, "TrackBand"),
    ("AirRing Smart Ring", "Wearables", 12999, 14, "AirRing"),
    ("SkyView 4K Drone", "Cameras & Drones", 45999, 11, "SkyView"),
    ("SnapShot Mirrorless Camera", "Cameras & Drones", 68999, 7, "SnapShot"),
    ("ActionCam Waterproof 4K", "Cameras & Drones", 13999, 33, "ActionCam"),
    ("ArcadePro Wireless Controller", "Gaming", 3999, 70, "ArcadePro"),
    ("NeonKeys Mechanical Keyboard", "Gaming", 6499, 40, "NeonKeys"),
    ("PixelView Gaming Monitor 27\"", "Gaming", 22999, 16, "PixelView"),
    ("QuantumSeat Gaming Chair", "Gaming", 17999, 13, "Quantum"),
    ("CoolBreeze Smart Air Purifier", "Home Appliances", 9999, 25, "CoolBreeze"),
    ("BrewMaster Smart Coffee Machine", "Home Appliances", 11999, 19, "BrewMaster"),
    ("CleanBot Robot Vacuum", "Home Appliances", 24999, 10, "CleanBot"),
    ("MeshLink WiFi 6 Router", "Networking", 8499, 38, "MeshLink"),
    ("SignalBoost Range Extender", "Networking", 2499, 60, "SignalBoost"),
    ("SwitchHub 8-Port Gigabit Switch", "Networking", 3299, 26, "SwitchHub"),
    ("PowerCell 20000mAh Power Bank", "Accessories", 1999, 150, "PowerCell"),
    ("GripStand Adjustable Laptop Stand", "Accessories", 1499, 6, "GripStand"),
]
ORDER_STATUSES = [
    "Pending",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled",
]
CUSTOMER_FIRST_NAMES = [
    "Riya", "Vikram", "Ishaan", "Meera", "Aditya", "Sanya", "Karan", "Neha", "Devika", "Farhan",
    "Priya", "Arjun", "Kavya", "Rahul", "Ananya", "Siddharth", "Pooja", "Rohit", "Divya", "Manish",
    "Tanya", "Nikhil", "Shreya", "Aman", "Ritika", "Yash", "Anjali", "Varun", "Sneha", "Karthik",
]
CUSTOMER_LAST_NAMES = [
    "Sharma", "Nair", "Kapoor", "Iyer", "Verma", "Malhotra", "Chopra", "Reddy", "Rao", "Ali",
    "Das", "Menon", "Gupta", "Singh", "Joshi", "Bhatia",
]


def seed_demo_marketplace() -> None:
    db = SessionLocal()
    try:
        already_seeded = db.query(User).filter(User.email == SEED_MARKER_EMAIL).first()
        if already_seeded:
            return

        rand = random.Random(42)
        now = datetime.now(timezone.utc)

        # --- Vendors ---
        vendor_users = []
        for i, v in enumerate(VENDORS):
            slug = v["business_name"].lower().replace(" ", "").replace(".", "").replace("&", "")
            user = User(
                id=uuid.uuid4(),
                email=f"contact@{slug}.in",
                hashed_password=hash_password("Vendor@12345"),
                full_name=v["owner"],
                role=UserRole.VENDOR,
                business_name=v["business_name"],
                phone=f"+91 9{rand.randint(100000000, 999999999)}",
                address=f"{rand.randint(1, 200)} MG Road, {v['city']}, {v['state']}",
                city=v["city"],
                state=v["state"],
                category=PRODUCTS[(i * 3) % len(PRODUCTS)][1],
                gst_number=f"{rand.randint(10, 37)}AAAAA{rand.randint(1000, 9999)}A1Z{rand.randint(1, 9)}",
                vendor_status=v["status"],
                commission_percent=v["commission"],
                rating=round(rand.uniform(3.6, 4.9), 1),
                is_active=v["status"] != VendorStatus.SUSPENDED,
            )
            db.add(user)
            vendor_users.append(user)
        db.flush()

        # --- Vendor product catalog (My Products) + mirrored analytics Product rows ---
        dataset = Dataset(
            id=uuid.uuid4(),
            original_filename="digitalhub_seed_marketplace.csv",
            stored_filename="digitalhub_seed_marketplace.csv",
            file_path="seed://digitalhub_seed_marketplace",
            file_type="csv",
            row_count=0,
            column_count=6,
            status=DatasetStatus.TRANSFORMED,
        )
        db.add(dataset)
        db.flush()

        vendor_products = []
        analytics_products = []
        for i, (name, category, price, stock, brand) in enumerate(PRODUCTS):
            vendor = vendor_users[i % len(vendor_users)]
            sku = f"DH-{brand.upper()[:4]}-{1000 + i}"

            vp = VendorProduct(
                id=uuid.uuid4(),
                vendor_id=vendor.id,
                name=name,
                category=category,
                description=f"{name} — genuine {brand} product, sold and shipped by {vendor.business_name}.",
                price=price,
                stock=stock,
                sku=sku,
                brand=brand,
                status=VendorProductStatus.ACTIVE,
            )
            db.add(vp)
            vendor_products.append(vp)

            ap = Product(
                id=uuid.uuid4(),
                dataset_id=dataset.id,
                vendor_id=vendor.id,
                product_ref=sku,
                name=name,
                category=category,
                total_units_sold=0,
                total_revenue=0.0,
                stock_quantity=stock,
            )
            db.add(ap)
            analytics_products.append(ap)
        db.flush()

        # --- Customers ---
        customers = []
        for i in range(45):
            first = CUSTOMER_FIRST_NAMES[i % len(CUSTOMER_FIRST_NAMES)]
            last = CUSTOMER_LAST_NAMES[rand.randint(0, len(CUSTOMER_LAST_NAMES) - 1)]
            customer = Customer(
                id=uuid.uuid4(),
                dataset_id=dataset.id,
                customer_ref=f"CUST-{2000 + i}",
                name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}{i}@example.com",
                total_orders=0,
                total_spent=0.0,
                avg_order_value=0.0,
            )
            db.add(customer)
            customers.append(customer)
        db.flush()

        # --- Orders: ~12 months of history across all products/customers ---
        orders = []
        for _ in range(380):
            product = rand.choice(analytics_products)
            customer = rand.choice(customers)
            quantity = rand.randint(1, 3)
            days_ago = rand.randint(0, 364)
            order_date = now - timedelta(days=days_ago, hours=rand.randint(0, 23))
            # Look up the matching seed price for this product.
            price = next(p for n, c, p, s, b in PRODUCTS if n == product.name)
            amount = round(price * quantity * rand.uniform(0.97, 1.0), 2)

            order = Order(
                id=uuid.uuid4(),
                dataset_id=dataset.id,
                customer_id=customer.id,
                product_id=product.id,
                order_ref=f"DH-ORD-{10000 + len(orders)}",
                order_date=order_date,
                quantity=quantity,
                amount=amount,
                status=rand.choice([
                    OrderStatus.PENDING,
                    OrderStatus.CONFIRMED,
                    OrderStatus.SHIPPED,
                    OrderStatus.DELIVERED,
                    OrderStatus.CANCELLED,
            ]),
            )
            db.add(order)
            orders.append(order)

            product.total_units_sold = (product.total_units_sold or 0) + quantity
            product.total_revenue = (product.total_revenue or 0.0) + amount
            customer.total_orders = (customer.total_orders or 0) + 1
            customer.total_spent = (customer.total_spent or 0.0) + amount
            if customer.first_purchase_date is None or order_date < customer.first_purchase_date:
                customer.first_purchase_date = order_date
            if customer.last_purchase_date is None or order_date > customer.last_purchase_date:
                customer.last_purchase_date = order_date

        for customer in customers:
            if customer.total_orders:
                customer.avg_order_value = round(customer.total_spent / customer.total_orders, 2)

        dataset.row_count = len(orders)

        db.commit()
        logger.info(
            "Seeded demo marketplace: %d vendors, %d products, %d customers, %d orders",
            len(vendor_users), len(PRODUCTS), len(customers), len(orders),
        )
    except Exception:
        db.rollback()
        logger.exception("Demo marketplace seeding failed — continuing without it")
    finally:
        db.close()
