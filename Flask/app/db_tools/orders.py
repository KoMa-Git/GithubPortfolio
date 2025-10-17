from extensions import db

# Orders model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationship to OrderItems
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total_amount={self.total_amount})>"

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.order_item_id} - Product {self.product_id}>"

# Data access functions