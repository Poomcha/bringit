import requests
from io import BytesIO

from app.db import get_db


def upload_image(image):
    url = "https://api.imgbb.com/1/upload"
    SECRET_KEY = "8134befc2e6b6afb4f3759102f291727"

    # Convert werkzeug.FileStorage image object to stream.
    data = image.read()
    stream = BytesIO(data)

    r = requests.post(url, files={"image": stream}, data={"key": SECRET_KEY})

    response = r.json()
    image_url = ""

    try:
        image_url = response["data"]["url"]
        thumb_url = response["data"]["thumb"]["url"]
        medium_url = response["data"]["medium"]["url"]
        delete_url = response["data"]["delete_url"]
    except Exception:
        return None
    else:
        return [image_url, thumb_url, medium_url, delete_url]


def delete_image(user_id):
    db = get_db()

    delete_url = db.execute(
        "SELECT delete_avatar_url FROM infos WHERE user_id = (?)", (user_id,)
    ).fetchone()["delete_avatar_url"]

    r = requests.post(delete_url)
    print(r)

    return
