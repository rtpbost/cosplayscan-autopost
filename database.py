import os
import random
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY
}

if SUPABASE_KEY.startswith("eyJ"):
    HEADERS["Authorization"] = f"Bearer {SUPABASE_KEY}"


def supabase_get(table, params=None, extra_headers=None):
    headers = HEADERS.copy()

    if extra_headers:
        headers.update(extra_headers)

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=headers,
        params=params or {},
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"Supabase error {response.status_code}: {response.text}"
        )

    return response


def get_posted_album_ids():
    response = supabase_get(
        "social_post_log",
        {
            "select": "album_id",
            "telegram_posted": "eq.true"
        }
    )

    rows = response.json()

    return {
        int(row["album_id"])
        for row in rows
        if row.get("album_id") is not None
    }


def get_album_count():
    response = supabase_get(
        "album",
        {
            "select": "id"
        },
        {
            "Prefer": "count=exact",
            "Range": "0-0"
        }
    )

    content_range = response.headers.get("Content-Range")

    if not content_range or "/" not in content_range:
        raise RuntimeError(
            f"Gagal membaca jumlah album. Content-Range: {content_range}"
        )

    total_text = content_range.split("/")[-1]

    if total_text == "*":
        raise RuntimeError("Supabase tidak mengembalikan total album.")

    return int(total_text)


def get_random_album():
    posted_ids = get_posted_album_ids()
    total_albums = get_album_count()

    if total_albums <= 0:
        raise RuntimeError("Tabel album kosong.")

    page_size = 100
    max_offset = max(0, total_albums - page_size)

    for _ in range(30):
        offset = random.randint(0, max_offset)

        response = supabase_get(
            "album",
            {
                "select": (
                    "id,title,cosplayer_name,"
                    "character_name,series_name"
                ),
                "order": "id.asc",
                "offset": offset,
                "limit": page_size
            }
        )

        albums = response.json()

        available = [
            album
            for album in albums
            if album.get("id") is not None
            and int(album["id"]) not in posted_ids
        ]

        if available:
            return random.choice(available)

    raise RuntimeError(
        "Tidak menemukan album yang belum pernah dipost."
    )


def get_album_photos(album_id):
    response = supabase_get(
        "photo",
        {
            "select": "id,image_url",
            "album_id": f"eq.{album_id}",
            "order": "id.asc"
        }
    )

    photos = response.json()

    photos = [
        photo
        for photo in photos
        if photo.get("image_url")
    ]

    return photos


def select_three_photos(photos):
    total = len(photos)

    if total == 0:
        return []

    if total <= 3:
        return [
            photo["image_url"]
            for photo in photos
        ]

    indexes = [
        0,
        total // 3,
        (total * 2) // 3
    ]

    return [
        photos[index]["image_url"]
        for index in indexes
    ]


def get_random_post():
    for _ in range(30):
        album = get_random_album()

        photos = get_album_photos(album["id"])
        photo_count = len(photos)

        if photo_count == 0:
            continue

        selected_photos = select_three_photos(photos)

        return {
            "album_id": album["id"],
            "title": album.get("title") or "Cosplay Album",
            "cosplayer_name": album.get("cosplayer_name"),
            "character_name": album.get("character_name"),
            "series_name": album.get("series_name"),
            "photo_count": photo_count,
            "photos": selected_photos,
            "album_url": (
                f"https://cosplayscan.asia/album/{album['id']}"
            )
        }

    raise RuntimeError(
        "Tidak menemukan album valid yang memiliki foto."
    )
