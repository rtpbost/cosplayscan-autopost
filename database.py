import os
import random
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


def supabase_get(table, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"

    headers = HEADERS.copy()
    headers["Prefer"] = "count=exact"

    response = requests.get(
        url,
        headers=headers,
        params=params or {},
        timeout=30
    )

    response.raise_for_status()
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
    return {int(row["album_id"]) for row in rows}


def get_random_album():
    posted_ids = get_posted_album_ids()

    # Ambil kandidat album secara acak dari beberapa halaman,
    # supaya tidak perlu download 7200+ album setiap posting.
    page_size = 100

    # cari jumlah album
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/album",
        headers={
            **HEADERS,
            "Prefer": "count=exact",
            "Range": "0-0"
        },
        params={
            "select": "id"
        },
        timeout=30
    )

    response.raise_for_status()

    content_range = response.headers.get("Content-Range", "")
    try:
        total_albums = int(content_range.split("/")[-1])
    except:
        raise RuntimeError(
            f"Gagal membaca jumlah album. Content-Range: {content_range}"
        )

    if total_albums == 0:
        raise RuntimeError("Tabel album kosong.")

    max_offset = max(0, total_albums - page_size)

    for _ in range(20):

        offset = random.randint(0, max_offset)

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/album",
            headers={
                **HEADERS,
                "Range": f"{offset}-{offset + page_size - 1}"
            },
            params={
                "select": "id,title,cosplayer_name,character_name,series_name",
                "order": "id.asc"
            },
            timeout=30
        )

        response.raise_for_status()
        albums = response.json()

        available = [
            album
            for album in albums
            if int(album["id"]) not in posted_ids
        ]

        if available:
            return random.choice(available)

    raise RuntimeError(
        "Tidak menemukan album yang belum pernah dipost."
    )


def get_album_photos(album_id):
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/photo",
        headers={
            **HEADERS,
            "Prefer": "count=exact"
        },
        params={
            "select": "id,image_url",
            "album_id": f"eq.{album_id}",
            "order": "id.asc"
        },
        timeout=30
    )

    response.raise_for_status()

    photos = response.json()

    if not photos:
        return [], 0

    return photos, len(photos)


def select_three_photos(photos):
    total = len(photos)

    if total == 0:
        return []

    if total == 1:
        return [photos[0]["image_url"]]

    if total == 2:
        return [
            photos[0]["image_url"],
            photos[1]["image_url"]
        ]

    indexes = [
        0,
        total // 3,
        (total * 2) // 3
    ]

    return [
        photos[i]["image_url"]
        for i in indexes
    ]


def get_random_post():
    for _ in range(20):

        album = get_random_album()

        photos, photo_count = get_album_photos(album["id"])

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
        "Tidak menemukan album valid dengan foto."
            )
