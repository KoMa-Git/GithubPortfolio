import csv
from db_tools.products import Product
from extensions import db

def load_products(csv_path):
    print("Loading seed products into in-memory DB...")
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