from functools import reduce
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from codequick import Route, Resolver 
from codequick.script import Settings

def deep_get(dictionary, keys, default=None):
	return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictionary)

def updateQueryParams(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

def get_images(item):
    url = f"https://akamaividz2.zee5.com/image/upload/resources/{deep_get(item, 'id')}"
    thumb = ""
    fanart=""
    if deep_get(item, "image.portrait") != "":
        thumb = f"{url}/portrait/{deep_get(item, 'image.portrait')}"
    if deep_get(item, "image.passport") != "":
        thumb = f"{url}/passport/{deep_get(item, 'image.passport')}"
    if deep_get(item, "image.list") != "":
        fanart = f"{url}/list/{deep_get(item, 'image.list')}"
    if deep_get(item, "image.listclean") != "":
        fanart = f"{url}/list_clean/{deep_get(item, 'image.listclean')}"
    return thumb, fanart


def get_deviceid():
    return Settings.get_string('device_id')

callback_urls = {
    "movie" : Resolver.ref("/resources/lib/main:play_video"),
    "tvshow" : Route.ref("/resources/lib/main:list_seasons"),
    "original" : Route.ref("/resources/lib/main:list_seasons")
}