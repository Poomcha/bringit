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

from marshmallow import ValidationError

from app.models.info import Info, InfoSchema
from app.models.user import User, UserSchema

from app.auth import signout

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
        from app.helpers.handle_image import upload_image, delete_image_user

        if avatar:
            if g.user["avatar_url"]:
                delete_image_user(g.user["id"])
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

        if not (
            g.user["firstname"].lower() == firstname.lower()
            and g.user["lastname"].lower() == lastname.lower()
        ):
            username = create_username(firstname, lastname)

        info = Info(
            user_id=g.user["id"],
            firstname=firstname,
            lastname=lastname,
            username=username,
            description=description,
            avatar_url=image_url,
            avatar_thumb_url=thumb_url,
            avatar_medium_url=medium_url,
            delete_avatar_url=delete_url,
        )
        infoSchema = InfoSchema()
        infoDict = infoSchema.dump(info)

        try:
            infoSchema.load(infoDict)
        except ValidationError as err:
            error = err.messages

        if error == None:
            # Generate username if necessary

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

        user = User(g.user["email"], password, confirmation)
        userSchema = UserSchema()
        userDict = userSchema.dump(user)

        try:
            userSchema.load(userDict)
        except ValidationError as err:
            error = err.messages

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


@bp.route("/delete/<int:user_id>", methods=["GET"])
@login_required
def delete(user_id):
    db = get_db()
    error = None

    if g.user["id"] == user_id:
        db.execute(
            """
            DELETE FROM users WHERE id = (?)
            """,
            (user_id,),
        )
        db.execute(
            """
            DELETE FROM infos WHERE user_id = (?)
            """,
            (g.user["id"]),
        )
        db.execute(
            """
            DELETE FROM lists_items WHERE list_id IN (
                SELECT list_id FROM lists_users
                    WHERE user_id = (?) AND right = (?)
            )
            """,
            (
                g.user["id"],
                "CREATOR",
            ),
        )
        db.execute(
            """
            DELETE FROM lists WHERE id IN (
                SELECT list_id FROM lists_users
                    WHERE user_id = (?) AND right = (?)
            )
            """,
            (
                g.user["id"],
                "CREATOR",
            ),
        )
        db.execute(
            """
            DELETE FROM items_users WHERE item_id IN (
                SELECT id FROM items WHERE creator_id = (?)
            )
            """,
            (g.user["id"]),
        )
        db.execute(
            """
            DELETE FROM items WHERE creator_id = (?)
            """,
            (g.user["id"],),
        )
        db.execute(
            """
            DELETE FROM users_users WHERE sender_id = (?) OR receiver_id = (?)
            """,
            (
                g.user["id"],
                g.user["id"],
            ),
        )
        db.execute(
            """
            DELETE FROM lists_users WHERE user_id = (?) AND right = (?)
            """,
            (
                g.user["id"],
                "CREATOR",
            ),
        )
        db.commit()
        signout()
    else:
        error = "You can't access this page."

    flash(error)

    return redirect(url_for("index.index"))
