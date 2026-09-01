import os
import requests

from formatter import build_caption

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_album(post):
    photos = post["photos"]

    if not photos:
        raise RuntimeError("Tidak ada foto untuk Telegram.")

    media = []

    for index, photo_url in enumerate(photos):
        item = {
            "type": "photo",
            "media": photo_url
        }

        if index == 0:
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
            f"Telegram error "
            f"{response.status_code}: {response.text}"
        )

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram API gagal: {result}"
        )

    messages = result.get("result", [])

    message_id = None

    if messages:
        message_id = messages[0].get("message_id")

    return {
        "success": True,
        "message_id": message_id,
        "raw": result
    }
