from database import get_random_post
from platforms.whatsapp import send_image
from formatter import build_caption


def main():
    print("Mengambil album untuk test WhatsApp...")

    post = get_random_post()

    print("Album ID :", post["album_id"])
    print("Title    :", post["title"])
    print("Photo    :", post["photos"][0])

    print("Mengirim 1 foto ke WhatsApp Channel...")

    result = send_image(
        post["photos"][0],
        build_caption(post)
    )

    print("WHATSAPP TEST SUCCESS")
    print(result)


if __name__ == "__main__":
    main()
