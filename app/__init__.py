import os

from flask import Flask

from werkzeug.security import generate_password_hash


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Will need a better SECRET_KEY eventually
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "bringit.sqlite"),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize db
    from . import db

    db.init_app(app)

    # Initialize mock data
    from app.helpers.mock_data import register_load_mock

    register_load_mock(app)

    # Register blueprints
    from . import auth, index, profile, bringers, lists, items

    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(bringers.bp)
    app.register_blueprint(lists.bp)
    app.register_blueprint(items.bp)

    return app
