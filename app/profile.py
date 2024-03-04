from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.auth import login_required, create_username, load_logged_in_user

bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    error = None
    db = get_db()

    if request.method == "POST":
        # Validation
        avatar = request.files["avatar-profile"]
        email = request.form["email-profile"].lower()
        firstname = request.form["firstname-profile"]
        lastname = request.form["lastname-profile"]
        description = request.form["description-profile"]
        username = g.user["username"]

        # Upload image to goopics.net
        from app.helpers.handle_image import upload_image, delete_image

        if avatar:
            if g.user["avatar_url"]:
                delete_image(g.user["id"])
            [image_url, thumb_url, medium_url, delete_url] = upload_image(avatar)
        else:
            if not g.user["avatar_url"]:
                [image_url, thumb_url, medium_url, delete_url] = [
                    None,
                    None,
                    None,
                    None,
                ]

        if not email:
            error = "You must provide a valid email."
        if not firstname:
            error = "You must provide a valid firstname."
        if not lastname:
            error = "You must provide a valid lastname."

        if error == None:
            # Generate username if necessary
            if not (
                g.user["firstname"].lower() == firstname.lower()
                and g.user["lastname"].lower() == lastname.lower()
            ):
                username = create_username(firstname, lastname)

            # Update db
            # Update email if necessary
            if g.user["email"].lower() != email.lower():
                db.execute(
                    "UPDATE users SET email = (?) WHERE id = (?)",
                    (
                        email,
                        g.user["id"],
                    ),
                )
            # Update infos
            if avatar:
                db.execute(
                    "UPDATE infos SET avatar_url = (?), avatar_thumb_url = (?), avatar_medium_url = (?), delete_avatar_url = (?), firstname = (?), lastname = (?), username = (?), description = (?) WHERE user_id = (?)",
                    (
                        image_url,
                        thumb_url,
                        medium_url,
                        delete_url,
                        firstname,
                        lastname,
                        username,
                        description,
                        g.user["id"],
                    ),
                )
            else:
                db.execute(
                    "UPDATE infos SET firstname = (?), lastname = (?), username = (?), description = (?) WHERE user_id = (?)",
                    (
                        firstname,
                        lastname,
                        username,
                        description,
                        g.user["id"],
                    ),
                )
            db.commit()

            # Reload g.user to apply changes directly
            load_logged_in_user()

        flash(error)

        return redirect(url_for("profile.profile"))

    return render_template("profile/profile.jinja")


@bp.route("/password", methods=["POST"])
@login_required
def password():
    error = None
    db = get_db()

    if request.method == "POST":
        # Validation

        old_password = request.form["old-password-profile"]
        password = request.form["password-profile"]
        confirmation = request.form["confirmation-profile"]

        user_password = db.execute(
            "SELECT password FROM users WHERE id = (?)", (g.user["id"],)
        ).fetchone()["password"]

        if password != confirmation:
            error = "Password and confirmation mismatch."
        if not check_password_hash(user_password, old_password):
            error = "Wrong old password."

        if error == None:
            # Update db
            db.execute(
                "UPDATE users SET password = (?) WHERE id = (?)",
                (
                    generate_password_hash(password),
                    g.user["id"],
                ),
            )
            db.commit()

        flash(error)

    return redirect(url_for("profile.profile"))
