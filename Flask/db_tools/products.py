from extensions import db

# Product model
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    image = db.Column(db.String(150))
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

# Data access functions
def get_all_products():
    return Product.query.all()

def get_product_by_id(product_id):
    return Product.query.get(product_id)

def add_product(name, description, image, price):
    product = Product(name=name, description=description, image=image, price=price)
    db.session.add(product)
    db.session.commit()
    return product
