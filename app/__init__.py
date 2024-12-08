from flask import Flask
from flask_session import Session
from decouple import config
from .utils import get_db_connection

def create_app():
    app = Flask(__name__)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = config('SECRET_KEY')  # Load secret key from .env

    Session(app)

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app
