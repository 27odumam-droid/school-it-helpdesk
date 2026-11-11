import os
from pathlib import Path

from flask import Flask

from helpdesk.db import close_db, initialize_database
from helpdesk.routes import register_routes


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "HELPDESK_DATABASE",
            str(Path(app.instance_path) / "helpdesk.sqlite3"),
        ),
        JSON_SORT_KEYS=False,
    )
    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    initialize_database(app)
    app.teardown_appcontext(close_db)
    register_routes(app)
    return app
