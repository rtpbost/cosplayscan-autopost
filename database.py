import os
import random
import requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY
}

if SUPABASE_KEY.startswith("eyJ"):
    HEADERS["Authorization"] = f"Bearer {SUPABASE_KEY}"


def request(method, table, params=None, json=None, extra_headers=None):
    headers = HEADERS.copy()

    if extra_headers:
        headers.update(extra_headers)

    response = requests.request(
        method,
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=headers,
        params=params,
        json=json,
        timeout=30
    )

    if not response.ok:
        raise RuntimeError(
            f"Supabase {method} {table} error "
            f"{response.status_code}: {response.text}"
        )

    return response


def get_log(album_id):
    response = request(
        "GET",
        "social_post_log",
        params={
            "select": "*",
            "album_id": f"eq.{album_id}",
            "limit": 1
        }
    )

    rows = response.json()
    return rows[0] if rows else None


def get_finished_album_ids():
    """
    Album dianggap selesai untuk pemilihan Telegram
    kalau telegram_posted sudah TRUE.
    """
    response = request(
        "GET",
        "social_post_log",
        params={
            "select": "album_id",
            "telegram_posted": "eq.true"
        }
    )

    return {
        int(row["album_id"])
        for row in response.json()
        if row.get("album_id") is not None
    }


def get_album_count():
    response = request(
        "GET",
        "album",
        params={
            "select": "id"
        },
        extra_headers={
            "Prefer": "count=exact",
            "Range": "0-0"
        }
    )

    content_range = response.headers.get("Content-Range")

    if not content_range or "/" not in content_range:
        raise RuntimeError(
            f"Tidak bisa membaca jumlah album: {content_range}"
        )

    total = content_range.split("/")[-1]

    if total == "*":
        raise RuntimeError("Supabase tidak memberikan total album.")

    return int(total)


def get_random_album():
    posted_ids = get_finished_album_ids()
    total = get_album_count()

    if total <= 0:
        raise RuntimeError("Tabel album kosong.")

    page_size = 100
    max_offset = max(0, total - page_size)

    for _ in range(50):
        offset = random.randint(0, max_offset)

        response = request(
            "GET",
            "album",
            params={
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

        candidates = [
            album
            for album in albums
            if album.get("id") is not None
            and int(album["id"]) not in posted_ids
        ]

        if candidates:
            return random.choice(candidates)

    raise RuntimeError(
        "Tidak menemukan album yang belum pernah dipost."
    )


def get_album_photos(album_id):
    response = request(
        "GET",
        "photo",
        params={
            "select": "id,image_url",
            "album_id": f"eq.{album_id}",
            "order": "id.asc"
        }
    )

    return [
        photo
        for photo in response.json()
        if photo.get("image_url")
    ]


def select_preview_photos(photos):
    total = len(photos)

    if total == 0:
        return []

    if total <= 3:
        return [
            photo["image_url"]
            for photo in photos
        ]

    # Tiga bagian berbeda dari album.
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
    for _ in range(50):
        album = get_random_album()
        photos = get_album_photos(album["id"])

        if not photos:
            continue

        return {
            "album_id": int(album["id"]),
            "title": album.get("title") or "Cosplay Album",
            "cosplayer_name": album.get("cosplayer_name"),
            "character_name": album.get("character_name"),
            "series_name": album.get("series_name"),
            "photo_count": len(photos),
            "photos": select_preview_photos(photos),
            "album_url": (
                f"https://cosplayscan.asia/album/{album['id']}"
            )
        }

    raise RuntimeError(
        "Tidak menemukan album valid yang memiliki foto."
    )


def ensure_log(album_id):
    existing = get_log(album_id)

    if existing:
        return existing

    response = request(
        "POST",
        "social_post_log",
        json={
            "album_id": album_id
        },
        extra_headers={
            "Prefer": "return=representation"
        }
    )

    rows = response.json()
    return rows[0] if rows else None


def mark_telegram_posted(album_id, message_id=None):
    ensure_log(album_id)

    now = datetime.now(timezone.utc).isoformat()

    request(
        "PATCH",
        "social_post_log",
        params={
            "album_id": f"eq.{album_id}"
        },
        json={
            "telegram_posted": True,
            "telegram_message_id": message_id,
            "telegram_posted_at": now
        },
        extra_headers={
            "Prefer": "return=minimal"
        }
    )


def mark_whatsapp_posted(album_id, post_id=None):
    ensure_log(album_id)

    now = datetime.now(timezone.utc).isoformat()

    request(
        "PATCH",
        "social_post_log",
        params={
            "album_id": f"eq.{album_id}"
        },
        json={
            "whatsapp_posted": True,
            "whatsapp_post_id": post_id,
            "whatsapp_posted_at": now
        },
        extra_headers={
            "Prefer": "return=minimal"
        }
        )
