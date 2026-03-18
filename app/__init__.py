import os

from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from app import models  # noqa: F401
from app.config import Config
from app.extensions import init_extensions
from app.routes.article_routes import article_bp
from app.routes.auth_routes import auth_bp
from app.routes.chat_routes import chat_bp
from app.routes.comment_routes import comment_bp
from app.routes.friendship_routes import friendship_bp
from app.routes.like_routes import like_bp
from app.routes.notification_routes import notification_bp
from app.routes.user_routes import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["AVATAR_UPLOAD_FOLDER"], exist_ok=True)

    init_extensions(app)
    CORS(app)

    app.register_blueprint(article_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(friendship_bp)
    app.register_blueprint(like_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(user_bp)

    @app.route("/")
    def home():
        return "Blog API running"

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        return {"error": "Fichier trop volumineux"}, 413

    return app
