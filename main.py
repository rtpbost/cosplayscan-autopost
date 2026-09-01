from database import (
    get_random_post,
    get_log,
    ensure_log,
    mark_telegram_posted
)

from platforms.telegram import send_album
from scheduler import run_scheduler


def post_once():
    print("\n==============================")
    print("COSPLAYSCAN AUTOPOST")
    print("==============================")

    post = get_random_post()

    album_id = post["album_id"]

    print("Album ID :", album_id)
    print("Title    :", post["title"])
    print("Photos   :", post["photo_count"])
    print("URL      :", post["album_url"])

    ensure_log(album_id)

    log = get_log(album_id)

    if log and log.get("telegram_posted"):
        print("Telegram sudah pernah dipost.")
        return

    print("Mengirim ke Telegram...")

    result = send_album(post)

    if result["success"]:
        mark_telegram_posted(
            album_id,
            result.get("message_id")
        )

        print("Telegram sukses.")
        print(
            "Message ID:",
            result.get("message_id")
        )


def main():
    print("CosplayScan Autopost starting...")
    run_scheduler(post_once)


if __name__ == "__main__":
    main()
