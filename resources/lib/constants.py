# -*- coding: utf-8 -*-
from resources.lib.utils import get_deviceid
from codequick.utils import urljoin_partial
import xbmc

# URLs
CONTENT_BASE_URL = "https://gwapi.zee5.com/content/"
VIDEO_BASE_URL = ""

if xbmc.getCondVisibility('System.Platform.Android'):
    USER_AGENT = "Mozilla/5.0 (Linux; Android 7.1.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
elif xbmc.getCondVisibility('System.Platform.Windows'):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
else:    
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

BASE_HEADERS = headers = {
	"Referer": "https://www.google.com/",
	"User-Agent": USER_AGENT
}

url_constructor = urljoin_partial(CONTENT_BASE_URL)

DEVICE_ID = get_deviceid()

DEFAULT_PARAMS = {
	"country" : "IN",
	"translation" : "en",
	"limit" : "24",
}

MAIN_MENU = [("ZEE TV", "collection/0-8-6813", "zeetv.webp"), ("MOVIES", "collection/0-8-7405", "movies.webp"), ("&Tv", "collection/0-8-6814", "andTv.webp"), ("Web Series", "collection/0-8-3z587419", "webseries.webp")]

URLS = {
	"VIDEO" : "https://spapi.zee5.com/singlePlayback/getDetails/secure",
}