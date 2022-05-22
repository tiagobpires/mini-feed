from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from spectree import SecurityScheme, SpecTree

import os
from config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = SpecTree(
    "flask",
    title="Mini Feed API",
    version="v.1.0",
    path="docs",
    security_schemes=[
        SecurityScheme(
            name="api_key",
            data={"type": "apiKey", "name": "Authorization", "in": "header"},
        )
    ],
    security={"api_key": []},
)


def create_app():
    app = Flask(__name__)

    environment = os.environ.get("ENVIRONMENT")

    if environment == "development":
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from models import User

    @jwt.user_lookup_loader
    def user_load(token, data):
        current_user = User.query.filter_by(username=data["sub"]).first()

        return current_user

    from controllers import auth_controller, user_controller, posts_controller

    app.register_blueprint(user_controller)
    app.register_blueprint(auth_controller)
    app.register_blueprint(posts_controller)

    api.register(app)

    return app
