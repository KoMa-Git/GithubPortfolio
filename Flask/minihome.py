from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import requests
import random

# initialize app, add secret key for session handling, session time limit, SQL server connection (use Render locally and memory for CI)
app = Flask(__name__)
app.secret_key = "somethingkrixkrax"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('RENDER_SQL','sqlite:///:memory:')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

# create db
db = SQLAlchemy(app)

# create model for users. (Could use table as well, probably that would be better for this basic app.)
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

# make a hashed password with Bcrypt. Keep as a string and not a byte for learning 
def get_password_hash(password):
    hashed_pwd = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt())
    return str(hashed_pwd)[2:-1]

# verify password, extended version in case if user created directly in SQL database and password form is not hashed
def verify_password(plain_password, hashed_password):
    try:
        if bcrypt.checkpw(bytes(plain_password, "utf-8"), bytes(hashed_password, "utf-8")):
            return True
        else:
            return False
    except:
        return False

# add the auth variable automatically to render templates 
@app.context_processor
def auth_user(): 
    if "auth" in session:
            return dict(auth=True)
    else:
        return dict(auth=False)

# lets get ready to rumble
@app.route("/")
def home():
    articles = []
    for i in range(5):
        quote_url = "https://api.spaceflightnewsapi.net/v4/articles/" + str(random.randint(30000,32000))
        try: 
            response = requests.get(quote_url, timeout=3)
        except:
            continue
        articles.append(response.json())
    return render_template("index.html", articles=articles)

@app.route("/about")
def about():
    quote_url = "https://fastapi-demo-iynq.onrender.com/get-a-quote"
    try: 
        response = requests.get(quote_url, timeout=3)
        quote = response.json()
        author = quote["author"]
        quote = quote["quote"]
    except:
        author = "Oscar Wilde"
        quote = "“Be yourself; everyone else is already taken.”"
    return render_template("about.html", author=author, quote=quote)

# this page is only for testing purpose, write out all records from table
@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST","GET"])
def login():
    # in case if we get here by POST
    if request.method == "POST":
        
        # store data coming back from form 
        email = request.form["email"]
        pwd = request.form["pwd"]

        # check database contains given email
        found_user = users.query.filter_by(email=email).first()
        
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
            found_user = users.query.filter_by(email=email).first()
            
            if found_user:
                # throw info email address is already registerd
                flash("Already registered with this email address", "info")
                # keep name and email for better UX
                return render_template("register.html", nm=name, email=email)
            
            else:
                # create a record to Model and add it to the database
                new_user = users(name, email, get_password_hash(password))
                db.session.add(new_user)
                db.session.commit()

                flash("Registered successfully! Please login.", "info")
                return redirect(url_for("login"))

    # in case if we get here by GET    
    else:
        
        # if session is alive 
        if "auth" in session:
            flash("You couldn't register if you are logged in", "info")
            return render_template("index.html")
        
        else:
            return render_template("register.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    # if session is alive
    if "user" in session:
        #store some session data and the user, identified by email as unique data
        name = session["user"]
        email = session["email"]
        user = users.query.filter_by(email=email).first()
        
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
                return redirect(url_for("home"))        
            else:
                # if DELETE confirmation fail then throw info
                flash(f"You didn't type DELETE correctly","info")

        return render_template("user.html", name=name, email=email)
    
    else:
        flash("You are not logged in!", "info")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    # inform user logout were successful
    flash("You logged out successfully!", "info")
    # and clear all session data
    session.pop("user", None)
    session.pop("email", None)
    session.pop("auth", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    # at the beginning create table if it doesn't exist already
    with app.app_context():
        db.create_all()
    # can use debug=True at development, then restart server automatically when save changes in code
    app.run()