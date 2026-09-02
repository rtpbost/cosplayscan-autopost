from database import (
    get_random_post,
    get_log,
    ensure_log,
    mark_telegram_posted
)

from platforms.telegram import send_album as send_telegram
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

    # TELEGRAM
    if log and log.get("telegram_posted"):
        print("Telegram sudah pernah dipost.")
    else:
        print("Mengirim ke Telegram...")

        result = send_telegram(post)

        if result["success"]:
            mark_telegram_posted(
                album_id,
                result.get("message_id")
            )

            print("Telegram sukses.")



def main():
    print("CosplayScan Autopost starting...")
    run_scheduler(post_once)


if __name__ == "__main__":
    main()
