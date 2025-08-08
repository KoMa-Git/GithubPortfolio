from flask_sqlalchemy import SQLAlchemy

# create a (shared) db object which could use separate files and initalize only in main app
db = SQLAlchemy()