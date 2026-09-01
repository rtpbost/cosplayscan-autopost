import os

WHAPI_ENABLED = (
    os.getenv("WHAPI_ENABLED", "false")
    .strip()
    .lower()
    == "true"
)


def is_enabled():
    return WHAPI_ENABLED


def send_album(post):
    if not WHAPI_ENABLED:
        return {
            "success": False,
            "skipped": True,
            "reason": "WHAPI disabled"
        }

    raise NotImplementedError(
        "Whapi.Cloud belum dikonfigurasi."
    )
