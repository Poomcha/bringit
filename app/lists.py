from flask import Blueprint, flash, g, redirect, render_template, request, url_for, json

from app.db import get_db
from app.auth import login_required
from app.helpers import handle_image

from app.forms.list import ListForm
from app.forms.item import ItemFormList

from datetime import datetime

bp = Blueprint("lists", __name__, url_prefix="/lists")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    db = get_db()

    list_ids = get_lists_id_for_user(db, g.user["id"])
    lists = [get_list_details(db, list_id["id"]) for list_id in list_ids]

    now = datetime.fromisoformat(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    my_lists = []
    my_bringers_lists = []
    old_lists = []

    for ls in lists:
        if datetime.fromisoformat(ls["expires_at"]) < now:
            old_lists.append(ls)
        else:
            if ls["creator_id"] == g.user["id"]:
                my_lists.append(ls)
            else:
                my_bringers_lists.append(ls)

    return render_template(
        "lists/index.jinja",
        my_lists=my_lists,
        my_bringers_lists=my_bringers_lists,
        old_lists=old_lists,
    )


@bp.route("/<int:list_id>", methods=["GET", "POST"])
@login_required
def list(list_id):
    db = get_db()

    ls = get_list_details(db, list_id)
    creator = get_user_infos(db, ls["creator_id"])
    items_id = [row["id"] for row in get_items_id_for_list(db, list_id)]
    items = [get_item_details(db, item_id) for item_id in items_id]
    items = [
        {
            "item_id": item_id,
            "details": [item for item in items if item["id"] == item_id][0],
            "users_id": get_users_id_for_items(db, item_id),
            "users_infos": [
                get_user_infos(db, user_id)
                for user_id in get_users_id_for_items(db, item_id)
            ],
        }
        for item_id in items_id
    ]
    return render_template(
        "lists/list.jinja",
        ls=ls,
        creator=creator,
        items=items,
        user_id=g.user["id"],
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    db = get_db()
    error = None

    my_bringers = get_bringers_for_user(db, g.user["id"])
    my_bringers = [
        (bringer["user_id"], f"{bringer['firstname']} {bringer['lastname']}")
        for bringer in my_bringers
    ]

    list_form = ListForm()
    item_form = ItemFormList()

    if request.method == "POST":
        form = ListForm(request.form)
        # Process list inputs
        post_list = {
            "creator_id": g.user["id"],
            "title": form.title.data,
            "description": form.description.data,
            "image": request.files["list_image"],
            "date": datetime.fromisoformat(form.date.raw_data[0]),
            "bringers": (
                [
                    bringer
                    for bringer in request.form.lists()
                    if bringer[0] == "list_bringers"
                ][0][1]
                if form.bringers.data
                else None
            ),
        }

        # Process items input
        post_items = [
            (input.split("_")[1], request.form[input])
            for input in request.form
            if input.startswith("itemform")
        ]
        post_items_processed = []
        for input in post_items:
            id = int(input[0].split("-")[1])
            try:
                post_items_processed[id].append(input)
            except IndexError:
                post_items_processed.append([input])
                post_items_processed[id].append(
                    (f"image-{id}", request.files[f"itemform-item_image-{id}"])
                )
        post_items_processed_dict = []
        for item in post_items_processed:
            temp = {}
            for attribute in item:
                temp.setdefault(f"{attribute[0].split('-')[0]}", attribute[1])
            post_items_processed_dict.append(temp)

        # Save list
        list_id = set_list(db, post_list, g.user["id"])

        # Save items
        [
            set_item_for_list(db, item, list_id, g.user["id"])
            for item in post_items_processed_dict
        ]

        return redirect(url_for("lists.index"))

    return render_template(
        "lists/create.jinja",
        list_form=list_form,
        item_form=item_form,
        my_bringers=my_bringers,
    )


@bp.route("/modify/<int:list_id>", methods=["GET", "POST"])
@login_required
def modify():
    db = get_db()

    list_form = ListForm()
    item_form = ItemFormList()

    my_bringers = get_bringers_for_user(db, g.user["id"])
    my_bringers = [
        (bringer["user_id"], f"{bringer['firstname']} {bringer['lastname']}")
        for bringer in my_bringers
    ]

    if request.method == "POST":
        return redirect(url_for("lists.index"))

    return render_template("lists/create.jinja")


def get_lists_id_for_user(db, user_id):
    lists = None

    lists = db.execute(
        """
        SELECT lists.id FROM lists 
            JOIN lists_users ON lists_users.list_id = lists.id 
                WHERE lists_users.user_id = (?)
        """,
        (user_id,),
    ).fetchall()

    return lists


def get_users_id_for_list(db, list_id):
    users_in_list = None

    users_in_list = db.execute(
        """
        SELECT lists_users.user_id FROM lists_users
            WHERE list_id = (?)
        """,
        (list_id,),
    ).fetchall()

    return users_in_lists


def get_items_id_for_list(db, list_id):
    items_in_list = None

    items_in_list = db.execute(
        """
        SELECT items.id FROM items
            JOIN lists_items ON items.id = lists_items.item_id
                WHERE lists_items.list_id = (?)
        """,
        (list_id,),
    ).fetchall()

    return items_in_list


def get_users_id_for_items(db, item_id):
    users_in_items = None

    users_in_items = db.execute(
        """
        SELECT items_users.user_id FROM items_users
            JOIN items ON items.id = items_users.item_id
                WHERE items_users.item_id = (?)
        """,
        (item_id,),
    ).fetchall()

    users_in_items = [user["user_id"] for user in users_in_items]

    return users_in_items


def get_list_details(db, list_id):
    details = None

    details = db.execute(
        """
        SELECT * FROM lists
            WHERE id = (?)
        """,
        (list_id,),
    ).fetchone()

    return details


def get_user_infos(db, user_id):
    infos = None

    infos = db.execute(
        """
        SELECT * FROM infos
            WHERE user_id = (?)
        """,
        (user_id,),
    ).fetchone()

    return infos


def get_item_details(db, item_id):
    details = None

    details = db.execute(
        """
        SELECT * FROM items
            WHERE id = (?)
        """,
        (item_id,),
    ).fetchone()

    return details


def get_bringers_for_user(db, user_id):
    bringers = None

    bringers = db.execute(
        """
            SELECT * FROM infos
                WHERE infos.user_id IN 
                    (
                        SELECT users_users.sender_id FROM users_users
                            WHERE users_users.receiver_id = (?) AND status = "ACCEPTED"
                                UNION
                        SELECT users_users.receiver_id FROM users_users
                            WHERE users_users.sender_id = (?) AND status = "ACCEPTED"
                    )
        """,
        (
            user_id,
            user_id,
        ),
    ).fetchall()

    return bringers


def set_list(db, post_list, user_id):
    # Handle image
    [image_url, thumb_url, medium_url, delete_url] = (
        handle_image.upload_image(post_list["image"])
        if post_list["image"]
        else [None, None, None, None]
    )
    new_list = {
        "creator_id": user_id,
        "title": post_list["title"],
        "description": post_list["description"],
        "list_url": image_url,
        "list_thumb_url": thumb_url,
        "list_medium_url": medium_url,
        "delete_list_url": delete_url,
        "expires_at": post_list["date"],
    }
    # Save list
    list_id = db.execute(
        """
        INSERT INTO lists (creator_id, title, description, list_url, list_thumb_url, list_medium_url, delete_list_url, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_list["creator_id"],
            new_list["title"],
            new_list["description"],
            new_list["list_url"],
            new_list["list_thumb_url"],
            new_list["list_medium_url"],
            new_list["delete_list_url"],
            new_list["expires_at"],
            datetime.now(),
            datetime.now(),
        ),
    ).lastrowid
    db.commit()

    # Save bringers
    post_list["bringers"].append(g.user["id"])
    for bringer in post_list["bringers"]:
        if bringer == g.user["id"]:
            set_user_for_list(db, bringer, list_id, "CREATOR")
        else:
            set_user_for_list(db, bringer, list_id, "INVITED")

    return list_id


def set_item_for_list(db, post_item, list_id, creator_id):
    # Handle image
    [item_url, item_thumb_url, item_medium_url, delete_item_url] = (
        handle_image.upload_image(post_item["image"])
        if post_item["image"]
        else [None, None, None, None]
    )
    # Save item
    item_id = db.execute(
        """
        INSERT INTO items 
            (creator_id, title, description, external_link, type, item_url, item_thumb_url, item_medium_url, delete_item_url, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            creator_id,
            post_item["title"],
            post_item["description"],
            post_item["url"],
            post_item["type"],
            item_url,
            item_thumb_url,
            item_medium_url,
            delete_item_url,
            datetime.now(),
            datetime.now(),
        ),
    ).lastrowid
    db.commit()
    # Save relationships
    db.execute(
        """
        INSERT INTO lists_items (list_id, item_id) VALUES (?, ?)
        """,
        (
            list_id,
            item_id,
        ),
    )
    db.commit()
    return


def set_user_for_list(db, user_id, list_id, right):
    db.execute(
        """
            INSERT INTO lists_users (user_id, list_id, right) VALUES (?, ?, ?)
        """,
        (
            user_id,
            list_id,
            right,
        ),
    )
    db.commit()
    return


def update_list(db, list_id):
    return


def update_item(db, item_id):
    return
