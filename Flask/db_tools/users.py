from extensions import db
import bcrypt

# create model for users. (Could use table as well, probably that would be better for this basic app.)
class User(db.Model):
    __tablename__ = 'users'

    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String)

# password functions
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

# Data access functions
def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_user(username, email, password):
    user = User(name=username, email=email, password = get_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user