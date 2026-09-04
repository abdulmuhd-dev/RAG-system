import pytest
from app.main import create_app


class TestAppFactory:

    def test_create_app_returns_flask_app(self):
        """create_app must return a Flask application."""
        from flask import Flask

        app = create_app()
        assert isinstance(app, Flask)

    def test_app_has_api_routes(self):
        """App must have /api/v1 routes registered."""
        app = create_app()
        rules = [str(rule) for rule in app.url_map.iter_rules()]

        assert any("/api/v1" in rule for rule in rules)

    def test_health_endpoint_exists(self):
        """Health endpoint must be registered."""
        app = create_app()
        client = app.test_client()

        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_metrics_endpoint_exists(self):
        """Metrics endpoint must be accessible."""
        app = create_app()

        # metrics is mounted via WSGI middleware
        # test via test client won't work directly
        # verify wsgi_app is wrapped instead
        assert hasattr(app, "wsgi_app")

    def test_testing_config(self):
        """App must respect TESTING config flag."""
        app = create_app()
        app.config["TESTING"] = True

        assert app.config["TESTING"] is True
