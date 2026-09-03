import logging

from flask import Flask
from flask_cors import CORS
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app.api.routes import api_bp
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory pattern.

    Mounts /metrics at the root level using WSGI middleware.
    This keeps /metrics separate from /api/v1/* routes
    and follows Prometheus convention exactly.
    """
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_bp, url_prefix="/api/v1")

    app.wsgi_app = DispatcherMiddleware(
        app.wsgi_app,
        {"/metrics": make_wsgi_app()}
    )

    logger.info("Flask app created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    settings = get_settings()
    host = settings.host
    port = settings.port
    debug = settings.debug
    app.run(host=host, port=port, debug=debug)
