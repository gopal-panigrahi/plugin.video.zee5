from __future__ import unicode_literals
from resources.lib.utils import updateQueryParams
import urlquick
from resources.lib.constants import BASE_HEADERS, DEVICE_ID, url_constructor
from codequick import Script
import re
import requests
import json


class Zee5API:
    def __init__(self):
        self.session = urlquick.Session()
        self.session.headers.update(BASE_HEADERS)
        self.token = self._getToken()
        self.session.headers.update(
            {"x-access-token": self.token, "Referer": "https://www.zee5.com/"}
        )

    def _getToken(self):
        url = "https://www.zee5.com/"
        resp = urlquick.get(url, headers=BASE_HEADERS)
        token = ""
        for t in re.findall(
            '"gwapiPlatformToken":"([^"]*)"', resp.content.decode("utf-8")
        ):
            if t != "":
                token = t
        return token

    def getCollection(self, url):
        resp = self.get(url)
        collection = resp and resp.get("buckets")[0].get("items")
        total = resp and resp.get("total")
        return collection, total

    def getSeasons(self, url):
        url = url_constructor(url)
        url = updateQueryParams(url, {"translation": "en", "country": "IN"})
        resp = self.get(url)
        return resp.get("seasons")

    def getEpisodes(self, url):
        url = url_constructor(url)
        episodes = self.get(url)
        return episodes

    def getVideo(self, url):
        payload = json.dumps(
            {"x-access-token": self.token, "X-Z5-Guest-Token": DEVICE_ID}
        )
        headers = {
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            "Accept": "application/json",
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "sec-ch-ua-platform": '"Linux"',
        }

        response = requests.request("POST", url, headers=headers, data=payload).json()

        return response.get("keyOsDetails"), response.get("assetDetails")

    def get(self, url, **kwargs):
        try:
            response = self.session.get(url, **kwargs)
            return response.json()
        except Exception as e:
            return self._handleError(e, url, "get", **kwargs)

    def post(self, url, **kwargs):
        try:
            response = self.session.post(url, **kwargs)
            return response.json()
        except Exception as e:
            return self._handleError(e, url, "post", **kwargs)

    def _handleError(self, e, url, _rtype, **kwargs):
        Script.notify("Internal Error", "")

    def _getPlayHeaders(self):
        stream_headers = self.session.headers
        return stream_headers
