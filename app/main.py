import logging

from flask import Flask
from flask_cors import CORS

from app.api.routes import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory pattern.

    WHY a factory function instead of a global app object?

      1. TESTING — tests call create_app() to get a fresh
         isolated instance. No shared state between tests.

      2. MULTIPLE CONFIGS — create_app("testing"),
         create_app("production") can behave differently.

      3. CIRCULAR IMPORTS — global app object causes import
         order issues in larger projects. Factory avoids this.

    This pattern is in virtually every production Flask codebase.
    """
    app = Flask(__name__)

    CORS(app)

    app.register_blueprint(api_bp, url_prefix="/api/v1")

    logger.info("Flask app created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=False)
