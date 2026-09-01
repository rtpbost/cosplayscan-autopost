def build_caption(post):
    return (
        f"{post['title']}\n"
        f"📸 {post['photo_count']} Photos\n\n"
        f"{post['album_url']}"
    )
