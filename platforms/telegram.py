import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def build_caption(post):
    return (
        f"{post['title']}\n"
        f"📸 {post['photo_count']} Photos\n\n"
        f"{post['album_url']}"
    )


def send_album(post):
    photos = post["photos"]

    if not photos:
        raise RuntimeError("Album tidak memiliki foto.")

    media = []

    for i, url in enumerate(photos):
        item = {
            "type": "photo",
            "media": url
        }

        if i == 0:
            item["caption"] = build_caption(post)

        media.append(item)

    response = requests.post(
        f"{API_BASE}/sendMediaGroup",
        json={
            "chat_id": CHANNEL_ID,
            "media": media
        },
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Telegram error {response.status_code}: {response.text}"
        )

    return response.json()
