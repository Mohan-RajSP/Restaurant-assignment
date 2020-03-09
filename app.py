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
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'

    # Initialize Plugins
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()
        from Authentication import auth_bp
        from Authentication.auth_view import github_blueprint
        from Restaurant import restaurant_bp

        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(github_blueprint, url_prefix="/githubLogin")
        app.register_blueprint(restaurant_bp, url_prefix="/restaurant")

        @app.before_first_request
        def create_table():
            db.create_all()

        from utils import custom_log
        from sqlalchemy import exc
        from marshmallow import ValidationError
        logger = custom_log(__name__)

        @app.errorhandler(Exception)
        def handle_Exception(error):
            logger.exception("The exception is {}".format(error))
            if "args" in dir(error):
                return {"message":"Exception occured", "Error":error.args},500
            return {"message": "Exception occured", "Error": error.args}, 500

        @app.errorhandler(exc.ProgrammingError)
        def programmingError(error):
            logger.exception("The exception is {}".format(error))
            return {"message": "Exception occured", "Error": error.args},424

        @app.errorhandler(exc.IntegrityError)
        def integrityError(error):
            db.session.rollback()
            logger.exception("The exception is {}".format(error))
            return {"message": "Exception occured", "Error": error.args}, 424

        @app.errorhandler(ValidationError)
        def validationError(error):
            db.session.rollback()
            logger.exception("The exception is {}".format(error))
            return {"message": "Validation Error Occured", "Error": error.args},400


    return app


if __name__ == "__main__":
    app=create_app()
    app.run(port=5000, debug=True)
