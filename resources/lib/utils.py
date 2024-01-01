from functools import reduce
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from codequick import Route, Resolver
from codequick.script import Settings


def deep_get(dictionary, keys, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )


def update_query_params(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def get_images(item):
    url = f"https://akamaividz2.zee5.com/image/upload/resources/{deep_get(item, 'id')}"
    thumb = get_thumbnail(url, item.get("image"))
    fanart = get_poster(url, item.get("image"))
    return thumb, fanart


def get_thumbnail(url, item):
    img = item.get("cover")
    if img:
        return f"{url}/portrait/{img}"
    return get_poster(url, item)


def get_poster(url, item):
    images = [
        "list",
        "cover",
        "portrait",
        "passport",
        "listclean",
    ]
    for image in images:
        img_id = item.get(image)
        if img_id:
            return f"{url}/{image}/{img_id}"
    return None


def get_device_id():
    return Settings.get_string("device_id")


def is_premium(item):
    businessType = deep_get(item, "businessType")
    if "premium" in businessType or "tvod" in businessType:
        return "(Premium)"
    return ""


callback_urls = {
    "movie": Resolver.ref("/resources/lib/main:play_video"),
    "external_link": Resolver.ref("/resources/lib/main:play_video"),
    "video": Resolver.ref("/resources/lib/main:play_video"),
    "tvshow": Route.ref("/resources/lib/main:list_seasons"),
    "original": Route.ref("/resources/lib/main:list_seasons"),
    "episode": Resolver.ref("/resources/lib/main:play_video"),
    "Manual": Route.ref("/resources/lib/main:list_collection"),
}
