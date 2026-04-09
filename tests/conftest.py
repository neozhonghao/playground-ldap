"""
Test configuration and fixtures
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def app():
    """Create Flask application for testing"""
    import os
    os.environ['FLASK_ENV'] = 'development'
    os.environ['RATELIMIT_STORAGE_URL'] = 'memory://'
    os.environ['SESSION_TYPE'] = 'filesystem'
    
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    flask_app.config['SESSION_TYPE'] = 'filesystem'
    return flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI test runner"""
    return app.test_cli_runner()
