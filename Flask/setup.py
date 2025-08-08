from minihome import app, db
from seed.load_products import load_products
from db_tools.products import Product
import os

def setup_app():
    with app.app_context():
        db.create_all()
        if not Product.query.all():
            load_products(os.path.join(os.path.dirname(__file__), 'seed', 'products.csv'))