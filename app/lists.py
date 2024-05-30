from flask import Blueprint, flash, g, redirect, render_template, request, url_for, json

from app.db import get_db
from app.auth import login_required
from app.helpers import handle_image

from datetime import datetime

from app.models.list import List, ListSchema
from app.models.items import Item, ItemSchema

from marshmallow import ValidationError

bp = Blueprint("lists", __name__, url_prefix="/lists")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    db = get_db()

    list_ids = get_lists_id_for_user(db, g.user["id"])
    lists = [get_list_details(db, list_id["id"]) for list_id in list_ids]

    for row in list_ids:
        print(row)

    now = datetime.fromisoformat(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

    my_lists = []
    my_bringers_lists = []
    old_lists = []

    for ls in lists:
        if ls["expires_at"] and datetime.fromisoformat(ls["expires_at"]) < now:
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
        user_id=g.user["id"],
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

    if request.method == "POST":
        form = request.form

        # Process list inputs
        post_list = process_list_input(form, request.files)

        # # Process items input
        post_items = process_item_input(form, request.files)

        # Save list
        list_id = set_list(db, post_list, g.user["id"])

        # Save items
        if list_id:
            [set_item_for_list(db, item, list_id, g.user["id"]) for item in post_items]
        else:
            return redirect(url_for("lists.create"))

        return redirect(url_for("lists.index"))

    return render_template(
        "lists/create.jinja",
        my_bringers=my_bringers,
    )


@bp.route("/modify/<int:list_id>", methods=["GET", "POST"])
@login_required
def modify(list_id):
    db = get_db()

    # Request initial datas
    current_list = get_list_details(db, list_id)
    current_bringers_id = [
        bringer["user_id"] for bringer in get_users_id_for_list(db, list_id)
    ]
    current_bringers = [get_user_infos(db, user_id) for user_id in current_bringers_id]
    current_items = [
        get_item_details(db, item["id"]) for item in get_items_id_for_list(db, list_id)
    ]

    my_bringers = get_bringers_for_user(db, g.user["id"])
    my_bringers = [
        (bringer["user_id"], f"{bringer['firstname']} {bringer['lastname']}")
        for bringer in my_bringers
    ]

    if request.method == "POST":
        form = request.form
        files = request.files

        # Process form
        post_list = process_list_input(form, files)
        post_items = process_item_input(form, files)

        # Delete removed items
        current_items_ids = [item["id"] for item in get_items_id_for_list(db, list_id)]
        to_save_items_ids = [
            int(item["id"]) for item in post_items if "id" in item.keys()
        ]
        for item_id in current_items_ids:
            if item_id not in to_save_items_ids:
                remove_item(db, item_id)
        # Save list and items
        update_list(db, post_list, list_id, g.user["id"], current_bringers_id)
        [update_item(db, item, list_id, g.user["id"]) for item in post_items]

        return redirect(url_for("lists.index"))

    return render_template(
        "lists/create.jinja",
        list_id=list_id,
        my_bringers=my_bringers,
        current_list=current_list,
        current_bringers_id=current_bringers_id,
        current_bringers=current_bringers,
        current_items=current_items,
    )


@bp.route("/delete/<int:list_id>", methods=["GET"])
@login_required
def delete(list_id):
    db = get_db()
    error = None

    list_user_infos = db.execute(
        """
        SELECT * FROM lists_users 
            WHERE list_id = (?) AND user_id = (?)
        """,
        (
            list_id,
            g.user["id"],
        ),
    ).fetchone()

    if list_user_infos["right"] == "CREATOR":
        handle_image.delete_image_list(list_id)
        db.execute(
            """
            DELETE FROM lists WHERE id = (?)
            """,
            (list_id,),
        )
        db.commit()
        db.execute(
            """
            DELETE FROM items_users
                WHERE item_id 
                    IN (
                        SELECT item_id 
                            FROM lists_items 
                                WHERE list_id = (?)
                    )
            """,
            (list_id,),
        )
        db.commit()

        # Delete related item image
        items_ids = [item["id"] for item in get_items_id_for_list(db, list_id)]
        [remove_item(db, item_id) for item_id in items_ids]

        db.execute(
            """
            DELETE FROM lists_items
                WHERE list_id = (?)
            """,
            (list_id,),
        )
        db.commit()

        # Delete lists_users relations
        db.execute(
            """
            DELETE FROM lists_users
                WHERE list_id = (?)
            """,
            (list_id,),
        )
        db.commit()

    return redirect(url_for("lists.index"))


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

    return users_in_list


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


def set_list(db, post_list, user_id, modify=False):
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
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    ls = List(
        new_list["creator_id"],
        new_list["title"],
        new_list["description"],
        new_list["list_url"],
        new_list["list_thumb_url"],
        new_list["list_medium_url"],
        new_list["delete_list_url"],
        new_list["created_at"],
        new_list["updated_at"],
        new_list["expires_at"],
    )
    lsSchema = ListSchema()
    lsDict = lsSchema.dump(ls)

    try:
        lsSchema.load(lsDict)
    except ValidationError as err:
        flash(err.messages)
    else:
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
                new_list["created_at"],
                new_list["updated_at"],
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

    return None


def set_item_for_list(db, post_item, list_id, creator_id, modify=False):
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


def remove_user_for_list(db, user_id, list_id):
    db.execute(
        """
        DELETE FROM lists_users
            WHERE user_id = (?) AND list_id = (?)
        """,
        (
            user_id,
            list_id,
        ),
    )
    db.commit()
    return


def remove_item(db, item_id):
    handle_image.delete_image_item(item_id)
    db.execute(
        """
        DELETE FROM items
            WHERE id = (?)
        """,
        (item_id,),
    )
    db.commit()
    return


def process_list_input(form, files):
    post_list = {
        "creator_id": g.user["id"],
        "title": form["list_title"],
        "description": form["list_description"],
        "image": files["list_image"],
        "date": form["list_date"],
        "bringers": (
            (form.to_dict(flat=False)["list_bringers"])
            if "list_bringers" in form.keys()
            else []
        ),
    }
    return post_list


def process_item_input(form, files):
    post_items = [
        (input.split("_")[1], form[input])
        for input in request.form
        if input.startswith("item")
    ]
    post_items_processed = []
    for input in post_items:
        id = int(input[0].split("-")[1])
        try:
            post_items_processed[id].append(input)
        except IndexError:
            post_items_processed.append([input])
            post_items_processed[id].append((f"image-{id}", files[f"item_image-{id}"]))
    post_items_processed_dict = []
    for item in post_items_processed:
        temp = {}
        for attribute in item:
            temp.setdefault(f"{attribute[0].split('-')[0]}", attribute[1])
        post_items_processed_dict.append(temp)

    return post_items_processed_dict


def update_list(db, post_list, list_id, user_id, bringers):
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
        "expires_at": post_list["date"],
    }
    # Save list
    if image_url:
        # Delete old image
        handle_image.delete_image_list(list_id)
        # Update new image
        db.execute(
            """
            UPDATE lists
                SET list_url  = (?),
                    list_medium_url = (?),
                    list_thumb_url = (?),
                    delete_list_url = (?)
                        WHERE id = (?)
            """,
            (
                image_url,
                medium_url,
                thumb_url,
                delete_url,
                list_id,
            ),
        )
        db.commit()

    db.execute(
        """
        UPDATE lists
            SET title = (?),
                description = (?),
                expires_at = (?),
                updated_at = (?)
                    WHERE id = (?)
        """,
        (
            new_list["title"],
            new_list["description"],
            new_list["expires_at"],
            datetime.now(),
            list_id,
        ),
    )
    db.commit()

    # Handle bringers
    for bringer_id in post_list["bringers"]:
        if bringer_id not in bringers and bringer_id != user_id:
            set_user_for_list(db, bringer_id, list_id, "INVITED")
    for bringer_id in bringers:
        if str(bringer_id) not in post_list["bringers"] and bringer_id != user_id:
            remove_user_for_list(db, bringer_id, list_id)

    return


def update_item(db, item, list_id, user_id):
    if "id" in item.keys():
        if item["image"]:
            # Handle image
            [item_url, item_thumb_url, item_medium_url, delete_item_url] = (
                handle_image.upload_image(item["image"])
            )
            # Delete old image
            handle_image.delete_image_item(item["id"])
            # Update new image
            db.execute(
                """
                UPDATE items
                    SET item_url  = (?),
                        item_medium_url = (?),
                        item_thumb_url = (?),
                        delete_item_url = (?)
                            WHERE id = (?)
                """,
                (
                    image_url,
                    medium_url,
                    thumb_url,
                    delete_url,
                    item["id"],
                ),
            )
            db.commit()

        db.execute(
            """
            UPDATE items
                SET title = (?),
                    description = (?),
                    external_link = (?),
                    type = (?),
                    updated_at = (?)
                    WHERE id = (?)
            """,
            (
                item["title"],
                item["description"],
                item["url"],
                item["type"],
                datetime.now(),
                item["id"],
            ),
        )
        db.commit()
    else:
        set_item_for_list(db, item, list_id, user_id)
    return
