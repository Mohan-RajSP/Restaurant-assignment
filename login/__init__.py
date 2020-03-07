from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    """Construct the core app object."""
    app = Flask(__name__, instance_relative_config=False)

    # Application Configuration
    app.config.from_object('config.Config')

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Initialize Plugins
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        #from . import routes
        from .Authentication import auth_bp, github_blueprint
        from .Restaurant import restaurant_bp
        # Register Blueprints
        #app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(github_blueprint, url_prefix="/githubLogin")
        app.register_blueprint(restaurant_bp, url_prefix="/restaurant")

        # Create Database Models
        db.create_all()

        return app