"""Composition root — monta a aplicação Flask (config, DB, blueprints, error handlers)."""
import logging
from datetime import datetime, timezone

from flask import Flask, jsonify
from flask_cors import CORS

from config import settings
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from middlewares.error_handler import register_error_handlers


def create_app():
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))})

    @app.route('/')
    def index():
        return jsonify({'message': 'Task Manager API', 'version': '1.0'})

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
