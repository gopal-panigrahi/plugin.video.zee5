from resources.lib.utils import get_deviceid
from codequick.utils import urljoin_partial
import xbmc

# URLs
CONTENT_BASE_URL = "https://gwapi.zee5.com/content/"
VIDEO_BASE_URL = ""

if xbmc.getCondVisibility("System.Platform.Android"):
    USER_AGENT = "Mozilla/5.0 (Linux; Android 7.1.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
elif xbmc.getCondVisibility("System.Platform.Windows"):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
else:
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

BASE_HEADERS = headers = {
    "Referer": "https://www.google.com/",
    "User-Agent": USER_AGENT,
}

url_constructor = urljoin_partial(CONTENT_BASE_URL)

DEVICE_ID = get_deviceid()

DEFAULT_PARAMS = {
    "country": "IN",
    "translation": "en",
    "limit": "24",
}

MAIN_MENU = [
    ("Home", "0-8-homepage", "home.png"),
    ("TV Shows", "0-8-tvshows", "tv.png"),
    ("Movies", "0-8-movies", "movies.png"),
    ("Music", "0-8-2707", "musical.png"),
    ("Zee Originals", "0-8-zeeoriginals", "originals.png"),
]

URLS = {
    "PAGE": "https://artemis.zee5.com/artemis/graphql",
    "VIDEO": "https://spapi.zee5.com/singlePlayback/getDetails/secure",
}
