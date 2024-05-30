import functools

from marshmallow import ValidationError

from random import randrange

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
from app.models.user import User, UserSchema
from app.models.info import Info, InfoSchema

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_prohibited(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            return redirect(url_for("index.index"))

        return view(**kwargs)

    return wrapped_view


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("index.index"))

        return view(**kwargs)

    return wrapped_view


def create_username(firstname, lastname):
    username = f"{firstname.lower()}.{lastname.lower()}#{randrange(0, 999)}"
    db = get_db()
    usernames = [
        item["username"]
        for item in db.execute(
            "SELECT username FROM infos WHERE username = (?)", (username,)
        ).fetchall()
    ]
    if username in usernames:
        return create_username(firstname, lastname)
    else:
        return username


@bp.route("/", methods=["GET"])
@login_prohibited
def auth():
    return render_template("auth/auth.jinja")


@bp.post("/signup")
@login_prohibited
def signup():

    email = request.form["email"].lower()
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    password = request.form["password"]
    confirmation = request.form["confirmation"]

    db = get_db()
    error = None

    user = User(email=email, password=password, confirmation=confirmation)
    userSchema = UserSchema()
    userDict = userSchema.dump(user)

    info = {"firstname": firstname, "lastname": lastname}
    infoSchema = InfoSchema()
    infoDict = infoSchema.dump(info)

    # Validate user and infos
    if user.password != user.confirmation:
        error = "Password and confirmation mismatch!"
    try:
        userVal = userSchema.load(userDict)
        infoVal = infoSchema.load(infoDict)
    except ValidationError as err:
        error = err.messages

    if error is None:
        try:
            db.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (
                    email,
                    generate_password_hash(password),
                ),
            )
            print("Got here")
            user_id = db.execute(
                "SELECT id FROM users WHERE email = (?)", (email,)
            ).fetchone()["id"]
            print("Got there")
            db.execute(
                "INSERT INTO infos (firstname, lastname, user_id, username) VALUES (?, ?, ?, ?)",
                (
                    firstname,
                    lastname,
                    user_id,
                    create_username(firstname, lastname),
                ),
            )
            print("Got there too")
            db.commit()
            print("Data commited")
        except db.IntegrityError:
            error = f"Email {email} is already registered."
        else:
            return signin()

    flash(error)

    return redirect(url_for("auth.auth"))


@bp.post("/signin")
@login_prohibited
def signin():

    email = request.form["email"]
    password = request.form["password"]

    db = get_db()
    error = None

    user = User(email=email, password=password, confirmation=password)
    userSchema = UserSchema()
    userDict = userSchema.dump(user)

    try:
        userVal = userSchema.load(userDict)
    except ValidationError as err:
        error = err.messages

    user = db.execute("SELECT * FROM users WHERE email = (?)", (email,)).fetchone()

    if user is None:
        error = "Invalid email."
    elif not check_password_hash(user["password"], password):
        # Unclear if password protected in front
        error = "Invalid password."

    if error is None:
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("index.index"))

    flash(error)

    return redirect(url_for("auth.auth"))


@bp.before_app_request
def load_logged_in_user():
    """Bind infos on user if logged in to each request"""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute(
                "SELECT users.id, users.email, infos.firstname, infos.lastname, infos.avatar_url, infos.avatar_thumb_url, infos.avatar_medium_url, infos.username, infos.description FROM users JOIN infos ON users.id = infos.user_id WHERE users.id = (?)",
                (user_id,),
            )
            .fetchone()
        )


@bp.route("/logout")
def signout():
    session.clear()
    return redirect(url_for("index.index"))
