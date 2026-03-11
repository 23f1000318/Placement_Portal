from flask import Flask
from application.database import db
from application.models import User

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.sqlite3"
    db.init_app(app)
    app.app_context().push()
    
    # Initialize database and create admin user if not exists
    db.create_all()
    admin_exists = User.query.filter_by(type="admin").first()
    if not admin_exists:
        admin_user = User(
            username="admin",
            email="admin@placement.com",
            password="admin123",
            type="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with username: admin and password: admin123")
    
    return app

app = create_app()
from application.controllers import *

if __name__ == "__main__":
    app.run()
