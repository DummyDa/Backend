from flask import Flask
from flask_login import LoginManager
import os
from auth import auth_bp
from plants import plants_bp
from animals import animals_bp
from forms import forms_bp
from user import load_user
from navigation import data
from logging_config import setup_logging

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    setup_logging()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    @app.context_processor
    def inject_navigation():
        return data()
    app.register_blueprint(auth_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(animals_bp)
    app.register_blueprint(forms_bp)
 #   app.register_blueprint(navigation_bp)

    login_manager.init_app(app)
    #login_manager.user_loader = load_user
    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)
    return app

