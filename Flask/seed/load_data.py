import csv
from db_tools.products import Product
from db_tools.users import User, get_password_hash
from db_tools.orders import Order, OrderItem
from extensions import db
import random
from datetime import datetime, timedelta

def load_products(csv_path):
    print("Loading seed products into DB...")
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = Product(
                name=row['name'],
                description=row['description'],
                price=float(row['price']),
                image=row.get('image')
            )
            db.session.add(product)
        db.session.commit()
    return 1

def load_users(csv_path):
    print("Loading seed users into DB...")
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = User(
                name=row['name'],
                email=row['email'],
                password=get_password_hash(row['password'])
            )
            db.session.add(user)
        db.session.commit()
    return 1

def load_order(cart):
    print("Loading seed order into DB...")

    total_amount = 0
    order_items_data = []
    
    # First collect data for Order
    for product_id, cart_item in cart.items():
        product = db.session.get(Product, product_id)
        # skip not valid products
        if not product:
            continue
        
        quantity = cart_item["quantity"]
        subtotal = product.price * quantity

        # append this item to the list
        order_items_data.append((product, quantity, subtotal))

        total_amount += subtotal

    # create Order object from these data with random user id
    #user_id = random.randint(1,len(User.query.all())+1)
    #order = Order(user_id=user_id if user_id<=len(User.query.all()) else None,
    #              total_amount=total_amount)
    order = Order(user_id=3,
                  order_date=generate_random_datetime(datetime(2023,1,1),datetime(2025,8,10)),
                  total_amount=total_amount)

    # add order to session
    db.session.add(order)
    db.session.commit() 

    # Then add ordered items to OrderItem
    for product, quantity, subtotal in order_items_data:
        order_item = OrderItem(
            order_id = order.id,
            product_id = product.id,
            quantity = quantity,
            price = product.price,
            subtotal = subtotal
        )
        db.session.add(order_item)
    
    db.session.commit()
    return 1


def generate_random_datetime(start_date, end_date):
    time_diff = end_date - start_date
    random_seconds = random.randint(0, int(time_diff.total_seconds()))
    random_date = start_date + timedelta(seconds=random_seconds)
    return random_date