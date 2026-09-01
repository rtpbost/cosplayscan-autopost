from database import get_random_post


def main():
    post = get_random_post()

    print("\n=== COSPLAYSCAN AUTOPOST TEST ===")
    print("Album ID :", post["album_id"])
    print("Title    :", post["title"])
    print("Photos   :", post["photo_count"])
    print("URL      :", post["album_url"])

    print("\n3 Preview:")
    for i, url in enumerate(post["photos"], start=1):
        print(f"{i}. {url}")


if __name__ == "__main__":
    main()
