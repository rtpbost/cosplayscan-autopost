from database import get_random_post
from platforms.telegram import send_album


def main():
    post = get_random_post()

    print("Posting album:")
    print("ID     :", post["album_id"])
    print("Title  :", post["title"])
    print("Photos :", post["photo_count"])

    result = send_album(post)

    print("Telegram sukses.")
    print(result)


if __name__ == "__main__":
    main()
