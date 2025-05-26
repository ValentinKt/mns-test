from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate
from config import Config  # Add this import

db = SQLAlchemy()
api = Api()
migrate = Migrate()

def create_app(config_class=Config):  # Use Config class here
    app = Flask(__name__)
    app.config.from_object(config_class)

    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debug line

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import init_routes
    init_routes(app)

    from app.resources import init_resources
    api_bp = init_resources(api)
    app.register_blueprint(api_bp)
    api.init_app(app)
    


    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
