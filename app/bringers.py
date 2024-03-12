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

bp = Blueprint("bringers", __name__, url_prefix="/bringers")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    db = get_db()
    error = None

    def bringer_request(db, status):
        return db.execute(
            "SELECT infos.user_id, infos.username, infos.firstname, infos.lastname, infos.avatar_thumb_url, infos.description FROM infos JOIN users_users ON users_users.receiver_id = infos.user_id WHERE users_users.status = (?) AND users_users.sender_id = (?)",
            (
                status,
                g.user["id"],
            ),
        ).fetchall()

    accepted = bringer_request(db, "ACCEPTED")
    pending = bringer_request(db, "PENDING")
    rejected = bringer_request(db, "REJECTED")
    ignored = bringer_request(db, "IGNORED")

    to_confirm = db.execute(
        "SELECT infos.user_id, infos.username, infos.firstname, infos.lastname, infos.avatar_thumb_url, infos.description FROM infos JOIN users_users ON users_users.sender_id = infos.user_id WHERE users_users.status = (?) AND users_users.receiver_id = (?)",
        (
            "PENDING",
            g.user["id"],
        ),
    ).fetchall()

    bringer = None
    if request.method == "POST":
        status = None
        username = request.form["username-bringers"]

        # Validation
        if not username:
            error = "You must provide an username."

        bringer = db.execute(
            "SELECT user_id, firstname, lastname, username, avatar_thumb_url, description FROM infos WHERE username = (?)",
            (username,),
        ).fetchone()

        if bringer:
            status = get_status(db, g.user["id"], bringer["user_id"])
        else:
            error = "Bringer not found, check username."

        flash(error)

    return render_template(
        "bringers/index.jinja",
        accepted=accepted,
        pending=pending,
        rejected=rejected,
        ignored=ignored,
        to_confirm=to_confirm,
        bringer=bringer,
    )


@bp.post("/add/<int:bringer_id>")
@login_required
def add(bringer_id):
    db = get_db()

    status = get_status(db, g.user["id"], bringer_id)
    if not status:
        db.execute(
            "INSERT INTO users_users (sender_id, receiver_id, status) VALUES (?, ?, ?)",
            (
                g.user["id"],
                bringer_id,
                "PENDING",
            ),
        )
        db.commit()

    return redirect(url_for("bringers.index"))


@bp.post("/cancel/<int:bringer_id>")
@login_required
def cancel(bringer_id):
    db = get_db()

    status = get_status(db, g.user["id"], bringer_id)
    if status == "PENDING":
        db.execute(
            "DELETE FROM users_users WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
            (
                g.user["id"],
                bringer_id,
                "PENDING",
            ),
        )
        db.commit()
    return redirect(url_for("bringers.index"))


@bp.post("/remove/<int:bringer_id>")
@login_required
def remove(bringer_id):
    db = get_db()

    status = get_status(db, g.user["id"], bringer_id)
    if status == "ACCEPTED":
        db.execute(
            "DELETE FROM users_users WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
            (
                g.user["id"],
                bringer_id,
                "ACCEPTED",
            ),
        )
        db.execute(
            "DELETE FROM users_users WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
            (
                bringer_id,
                g.user["id"],
                "ACCEPTED",
            ),
        )
        db.commit()
    return redirect(url_for("bringers.index"))


@bp.post("/accept/<int:bringer_id>")
@login_required
def accept(bringer_id):
    db = get_db()

    status = get_status(db, bringer_id, g.user["id"])
    if status == "PENDING":
        db.execute(
            "UPDATE users_users SET status = (?) WHERE sender_id = (?) AND receiver_id = (?)",
            (
                "ACCEPTED",
                bringer_id,
                g.user["id"],
            ),
        )
        db.execute(
            "INSERT INTO users_users (sender_id, receiver_id, status) VALUES (?, ?, ?)",
            (
                g.user["id"],
                bringer_id,
                "ACCEPTED",
            ),
        )
        db.commit()
    return redirect(url_for("bringers.index"))


@bp.post("/reject/<int:bringer_id>")
@login_required
def reject(bringer_id):
    db = get_db()

    status = get_status(db, bringer_id, g.user["id"])
    if status == "PENDING":
        db.execute(
            "UPDATE users_users SET status = (?) WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
            (
                bringer_id,
                g.user["id"],
                "PENDING",
            ),
        )
        db.commit()
    return redirect(url_for("bringers.index"))


@bp.post("/ignore/<int:bringer_id>")
@login_required
def ignore(bringer_id):
    db = get_db()

    status = get_status(db, bringer_id, g.user["id"])
    if not status:
        db.execute(
            "INSERT INTO users_users (sender_id, receiver_id, status) VALUES (?, ?, ?)",
            (
                g.user["id"],
                bringer_id,
                "IGNORED",
            ),
        )
        db.commit()
    elif status != "IGNORED":
        db.execute(
            "UPDATE users_users SET status = (?) WHERE sender_id = (?) AND receiver_id = (?)",
            (
                "IGNORED",
                bringer_id,
                g.user["id"],
            ),
        )
        db.commit()
    return redirect(url_for("bringers.index"))


@bp.post("/unignore/<int:bringer_id>")
@login_required
def unignore(bringer_id):
    db = get_db()

    status = get_status(db, bringer_id, g.user["id"])
    if status == "IGNORED":
        db.execute(
            "DELETE FROM users_users WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
            (
                bringer_id,
                g.user["id"],
                "IGNORED",
            ),
        )
        db.commit()
    else:
        status = get_status(db, g.user["id"], bringer_id)
        if status == "IGNORED":
            db.execute(
                "DELETE FROM users_users WHERE sender_id = (?) AND receiver_id = (?) AND status = (?)",
                (
                    g.user["id"],
                    bringer_id,
                    "IGNORED",
                ),
            )
            db.commit()
    return redirect(url_for("bringers.index"))


def get_status(db, sender_id, receiver_id):
    status = None
    status = db.execute(
        "SELECT status FROM users_users WHERE sender_id = (?) AND receiver_id = (?)",
        (
            sender_id,
            receiver_id,
        ),
    ).fetchone()
    if status:
        status = status["status"]
    return status


def get_username(db, bringer_id):
    username = None
    username = db.execute(
        "SELECT username FROM infos WHERE user_id = (?)",
        (bringer_id,),
    ).fetchone()
    if username:
        username = username["username"]
    return username
