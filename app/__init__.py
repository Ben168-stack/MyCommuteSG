from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes.views import views_bp
    from app.routes.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    return app
