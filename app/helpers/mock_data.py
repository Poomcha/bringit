import csv, click

from flask import current_app
from app.db import get_db
from app.auth import create_username

from werkzeug.security import generate_password_hash

GLOBAL_PASSWORD = "12345678"


@click.command("load-mock")
def load_mock_command():
    db = get_db()

    with current_app.open_resource("helpers/mock_data.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            db.execute(
                "INSERT INTO users (id, email, password) VALUES (?, ?, ?)",
                (
                    int(row["id"]),
                    row["email"],
                    generate_password_hash(GLOBAL_PASSWORD),
                ),
            )
            db.execute(
                "INSERT INTO infos (user_id, firstname, lastname, username) VALUES (?, ?, ?, ?)",
                (
                    int(row["id"]),
                    row["firstname"],
                    row["lastname"],
                    create_username(row["firstname"], row["lastname"]),
                ),
            )
            db.commit()

    print("Mock data loaded.")


def register_load_mock(app):
    app.cli.add_command(load_mock_command)
