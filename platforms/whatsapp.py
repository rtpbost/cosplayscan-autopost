import os
import requests

from formatter import build_caption

WHAPI_TOKEN = os.environ["WHAPI_TOKEN"]
WHAPI_CHANNEL_ID = os.environ["WHAPI_CHANNEL_ID"]

WHAPI_ENABLED = (
    os.getenv("WHAPI_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)

API_BASE = "https://gate.whapi.cloud"


def is_enabled():
    return WHAPI_ENABLED


def send_image(photo_url, caption=""):
    response = requests.post(
        f"{API_BASE}/messages/image",
        headers={
            "Authorization": f"Bearer {WHAPI_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "to": WHAPI_CHANNEL_ID,
            "media": photo_url,
            "caption": caption
        },
        timeout=60
    )

    if not response.ok:
        raise RuntimeError(
            f"Whapi error "
            f"{response.status_code}: {response.text}"
        )

    return response.json()


def send_album(post):
    if not WHAPI_ENABLED:
        return {
            "success": False,
            "skipped": True,
            "reason": "WHAPI disabled"
        }

    photos = post["photos"]

    if not photos:
        raise RuntimeError(
            "Tidak ada foto untuk WhatsApp."
        )

    results = []

    for index, photo_url in enumerate(photos):
        caption = ""

        if index == 0:
            caption = build_caption(post)

        result = send_image(
            photo_url,
            caption
        )

        results.append(result)

    post_id = None

    if results:
        first = results[0]

        if isinstance(first, dict):
            sent_message = first.get("sent_message", {})

            if isinstance(sent_message, dict):
                post_id = sent_message.get("id")

    return {
        "success": True,
        "post_id": post_id,
        "raw": results
    }
