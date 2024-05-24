from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from app.db import get_db
from app.auth import login_required
from app.lists import get_users_id_for_items

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.route("/register/<int:list_id>/<int:item_id>/<int:user_id>", methods=["POST"])
@login_required
def register(list_id, item_id, user_id):
    db = get_db()

    if (
        g.user["id"] not in get_users_id_for_items(db, item_id)
        and g.user["id"] == user_id
    ):

        db.execute(
            """
            INSERT INTO items_users (item_id, user_id)
                VALUES (?, ?)
            """,
            (
                item_id,
                user_id,
            ),
        )
        db.commit()

    return redirect(url_for("lists.list", list_id=list_id))


@bp.route("/unregister/<int:list_id>/<int:item_id>/<int:user_id>", methods=["POST"])
@login_required
def unregister(list_id, item_id, user_id):
    db = get_db()

    if g.user["id"] in get_users_id_for_items(db, item_id) and g.user["id"] == user_id:
        db.execute(
            """
            DELETE FROM items_users 
                WHERE item_id = (?) AND user_id = (?)
            """,
            (
                item_id,
                user_id,
            ),
        )
        db.commit()

    return redirect(url_for("lists.list", list_id=list_id))
