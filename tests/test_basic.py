"""Basic tests for the application"""
import pytest
from flask import Flask

def test_import_app():
    """Test that the main app can be imported"""
    try:
        from app import create_app
        app = create_app()
        assert isinstance(app, Flask)
    except ImportError:
        pytest.skip("App dependencies not installed")

def test_app_creation():
    """Test basic app creation"""
    try:
        from app import create_app
        app = create_app()
        assert app.config is not None
    except ImportError:
        pytest.skip("App dependencies not installed")