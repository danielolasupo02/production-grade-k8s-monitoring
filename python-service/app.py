import logging

from flask import Flask, jsonify

from .config import Config
from .metrics import start_resource_metrics_updater
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger = logging.getLogger(__name__)

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"status": "ERROR", "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"status": "ERROR", "message": "Method not allowed"}), 405

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unhandled exception")
        return jsonify({"status": "ERROR", "message": "Internal server error"}), 500

    start_resource_metrics_updater(app.config["RESOURCE_METRICS_INTERVAL_SEC"])

    logger.info("payment-service application initialized")
    return app