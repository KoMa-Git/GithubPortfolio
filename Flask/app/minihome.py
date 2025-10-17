from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from extensions import db
from db_tools.users import User, verify_password, add_user, get_password_hash
from db_tools.products import Product, get_product_by_id
from db_tools.orders import Order, OrderItem
from seed.load_data import load_products, load_users, load_order
import os
import requests
import random

# initialize app, add secret key for session handling, session time limit, SQL server connection (use Render locally and memory for CI)
# important note about session in session_decode.py
app = Flask(__name__)
app.secret_key = "somethingkrixkrax"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("RENDER_SQL", "sqlite:///:memory:")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

# initalize db 
db.init_app(app)

# add the auth variable automatically to render templates 
@app.context_processor
def auth_user(): 
    if "auth" in session:
        return dict(auth=True)
    else:
        return dict(auth=False)

# lets get ready to rumble
@app.route("/news")
def news():
    articles = []
    for i in range(5):
        quote_url = "https://api.spaceflightnewsapi.net/v4/articles/" + str(random.randint(30000,32000))
        try: 
            response = requests.get(quote_url, timeout=3)
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException as e:
            continue
        if "detail" in response.json():
            continue
        articles.append(response.json())
    print(articles)
    return render_template("news.html", articles=articles)

@app.route("/")
@app.route("/products")
def products():
    products = Product.query.all()
    return render_template("products.html", products=products)

# keep updated badge anytime when refresh or redirect to other page
@app.context_processor
def cart_total():
    return dict(total_items_in_cart=get_cart_item_count())

def get_cart_item_count():
    cart = session.get("cart", {})
    return sum(item["quantity"] for item in cart.values())

# add to cart function with JS and AJAX
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")

    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"status":"error", "message":"Product not found"}), 404

    cart = session.get("cart", {})

    # If product already in cart, increase quantity
    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] += 1
    else:
        cart[str(product_id)] = {
            "image": product.image,
            "name": product.name,
            "price": product.price,
            "quantity": 1
        }

    session["cart"] = cart
    return jsonify({
        "status":"success",
        "message": f"Added {product.name} to cart",
        "cartItemCount": sum(item["quantity"] for item in cart.values())
    })

# use JS and AJAX to update cart
@app.route("/update_cart", methods=["POST"])
def update_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    action = data.get("action")
    quantity = data.get("quantity")  # Optional, for "set"

    if not product_id or not action:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    cart = session.get("cart", None)
    product_key = str(product_id)

    if product_key not in cart:
        return jsonify({"status": "error", "message": "Product not in cart"}), 404

    if action == "increase":
        cart[product_key]["quantity"] += 1

    elif action == "decrease":
        cart[product_key]["quantity"] -= 1
        if cart[product_key]["quantity"] <= 0:
            del cart[product_key]
            session["cart"] = cart
            return jsonify({
                "status": "success",
                "message": "Product removed from cart",
                "cart": cart,
                "cartItemCount": sum(item["quantity"] for item in cart.values())
            })

    elif action == "set":
        try:
            qty = int(quantity)
            if qty <= 0:
                del cart[product_key]
                message = "Product removed from cart"
            else:
                cart[product_key]["quantity"] = qty
                message = f"Updated quantity to {qty}"
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid quantity"}), 400
    else:
        return jsonify({"status": "error", "message": "Unknown action"}), 400

    session["cart"] = cart

    return jsonify({
        "status": "success",
        "message": "Cart updated",
        "cart": cart,
        "cartItemCount": sum(item["quantity"] for item in cart.values())
    })

# cart page
@app.route("/cart")
def cart():
    cart = session.get("cart", None)
    return render_template("cart.html", cart=cart)

# minimal checkout, save order in db
@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", None)
    
    # handle if arrive to here with empty hands
    if not cart:
        flash("Your cart is empty", "info")
        return redirect(url_for("products"))
    
    total_amount = 0
    order_items_data = []
    email = session.get("email", None)
    found_user = User.query.filter_by(email=email).first()
    
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

    # create Order object from these data
    order = Order(user_id=found_user.id if found_user else None,
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

    user = session.get("user", "Client")
    print(session["cart"])
    session.pop("cart")
    return render_template("checkout.html", user=user)

# this page is only for testing purpose, write out all records from tables
@app.route("/view")
def view():
    orders = db.session.query(Order, User.name).join(User, isouter=True) # outer join to list anonym orders as well
    ordered_items = db.session.query(OrderItem, Product.name).join(Product)
    return render_template("view.html", users=User.query.all(), products=Product.query.all(), orders=orders, ordered_items=ordered_items)

@app.route("/login", methods=["POST","GET"])
def login():
    # in case if we get here by POST
    if request.method == "POST":
        
        # store data coming back from form 
        email = request.form["email"]
        pwd = request.form["pwd"]

        # check database contains given email
        found_user = User.query.filter_by(email=email).first()
        
        if found_user:
        
            # check user given password is matching with stored password in database
            if verify_password(pwd, found_user.password):
                # if yes then store some session data
                session.permanent = True
                session["email"] = found_user.email
                session["user"] = found_user.name
                session["auth"] = True
                
                flash(f"{found_user.name} logged in successful!", "info")
                return redirect(url_for("user"))
            else:
                # if not then throw an error message, hold email for better UX
                flash(f"Incorrect email or password!", "warning")
                return render_template("login.html", email=email)    
        
        # in case if couldn't find email in database 
        else:
            flash(f"Incorrect email or password!", "warning")
            return render_template("login.html", email=email)
    
    # in case if we get here by GET
    else:

        # if session is alive
        if "auth" in session:
            user = session["user"]
            flash(f"{user} already logged in!", "info")
            return redirect("/")
        
        return render_template("login.html")

@app.route("/register", methods=["POST","GET"])
def register():
    # in case if we get here by POST
    if request.method == "POST":
        
        # store data from form
        email = request.form["email"]
        name = request.form["nm"]
        password = request.form["pwd"]

        # check all fields are filled with some data
        if email =="" or name =="" or password=="":
            # if any of them was empty then throw a warning
            flash("All fields are required", "warning")
            # in case if name or email wasn't empty then keep data for better UX
            return render_template("register.html", nm=name, email=email)
        
        else:
            # check if email is already in database
            found_user = User.query.filter_by(email=email).first()
            
            if found_user:
                # throw info email address is already registerd
                flash("Already registered with this email address", "info")
                # keep name and email for better UX
                return render_template("register.html", nm=name, email=email)
            
            else:
                # create a record to Model and add it to the database
                add_user(name, email, password)
                flash("Registered successfully! Please login.", "info")
                return redirect(url_for("login"))

    # in case if we get here by GET    
    else:
        
        # if session is alive 
        if "auth" in session:
            flash("You couldn't register if you are logged in", "info")
            return render_template("products.html")
        
        else:
            return render_template("register.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    # if session is alive
    if "user" in session:
        #store some session data and the user, identified by email as unique data
        name = session["user"]
        email = session["email"]
        user = User.query.filter_by(email=email).first()
        
        
        # if user change his name on page
        if request.method == "POST" and "nm" in request.form:
            # then store new name
            name = request.form["nm"]
            # change user in session as well
            session["user"] = name
            # change name in database as well.
            user.name = name
            db.session.commit()
            flash("New name was saved","info")
        
        # if user changes password
        elif request.method == "POST" and "old_pass" in request.form:
            # store form data
            old_pass = request.form["old_pass"]
            new_pass = request.form["new_pass"]
            # check password fields are filled
            if old_pass =="" or new_pass =="":
                flash(f"Password fields cannot be empty!", "warning")
                return render_template("user.html", name=name, email=email)
            
            # and check old password is matching with database 
            if verify_password(old_pass, user.password):
                # if yes, then hash new passord and store it in database
                user.password = get_password_hash(new_pass)
                db.session.commit()
                flash(f"Password has changed","info")
            else:
                # if not then throw a warning
                flash(f"Your old password is not valid","warning")

        # if user delete account
        elif request.method == "POST" and "del" in request.form:
            # check user typed DELETE as confirmation of action
            if request.form["del"] == "DELETE":
                db.session.delete(user)
                db.session.commit()
                # clear all data from session, might could be better with loop
                session.pop("user", None)
                session.pop("email", None)
                session.pop("auth", None)
                flash(f"Account deleted","info")
                return redirect(url_for("products"))        
            else:
                # if DELETE confirmation fail then throw info
                flash(f"You didn't type DELETE correctly","info")

        # prevoius orders 
        orders = db.session.query(Order).filter_by(user_id=user.id)
        order_items = db.session.query(OrderItem, Product.name).join(Product)
        
        return render_template("user.html", name=name, email=email, orders=list(orders), order_items=order_items)
    
    else:
        flash("You are not logged in!", "info")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    if "auth" in session:
        # clear all session data
        session.pop("user", None)
        session.pop("email", None)
        session.pop("auth", None)
        cart = session.get("cart", None)
        if cart:
            session.pop("cart", None)
        # inform user logout were successful
        flash("You logged out successfully!", "info")
        return redirect(url_for("login"))
    else:
        flash("You were not logged in!", "info")
        return redirect(url_for("login"))

if __name__ == "__main__":
    # at the beginning create table if it doesn't exist already
    with app.app_context():
        db.create_all()
        if not Product.query.all():
            load_products(os.path.join(os.path.dirname(__file__), "seed", "products.csv"))
            load_users(os.path.join(os.path.dirname(__file__), "seed", "users.csv"))
            load_order({'3': {'image': 'rocket_brush.jpg', 'name': 'Rocket-Powered Toothbrush', 'price': 12.99, 'quantity': 1}, '4': {'image': 'cat_helmet.jpg', 'name': 'Galactic Cat Helmet', 'price': 19.95, 'quantity': 4}})
            load_order({'1': {'image': 'zero_g_coffee.jpg', 'name': 'Zero-G Coffee', 'price': 3.99, 'quantity': 1}, '2': {'image': 'alien_snack.jpg', 'name': 'Alien Snack Pack', 'price': 5.49, 'quantity': 1}, '3': {'image': 'rocket_brush.jpg', 'name': 'Rocket-Powered Toothbrush', 'price': 12.99, 'quantity': 1}})
        # can use debug=True at development, then restart server automatically when save changes in code
    
    app.run(host="0.0.0.0", port=8000)