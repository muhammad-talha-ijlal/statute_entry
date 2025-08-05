from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager      # NEW

db = SQLAlchemy()
login_manager = LoginManager()            # NEW
login_manager.login_view = "auth.login"   # redirect when not logged-in
