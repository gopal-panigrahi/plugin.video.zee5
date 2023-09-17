from __future__ import unicode_literals
from resources.lib.utils import updateQueryParams, deep_get
import urlquick
from resources.lib.constants import URLS, BASE_HEADERS, DEVICE_ID, url_constructor
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

    def getPage(self, id, page):
        payload = json.dumps(
            {
                "query": "\n  query ($id: ID!, $filter: CollectionFilter) {\n    collection(id: $id, filter: $filter) {\n      id\n      title\n      originalTitle\n      tags\n      rails {\n        id\n        title\n        originalTitle\n        tags\n        position\n        contents {\n          ... on Episode {\n            id\n            title\n            originalTitle\n            duration\n            upcomingContent\n            contentOwner\n            businessType\n            eventStartDate\n            genres {\n              id\n              value\n            }\n            languages\n            description\n            assetType\n            assetSubType\n            releaseDate\n            viewCount {\n              formattedCount\n              count\n            }\n            image {\n              list\n              cover\n              appCover\n              sticker\n              svodCover\n              verticalBanner\n              appSvodCover\n            }\n            actors\n            ageRating\n            audioLanguages\n            subtitleLanguages\n            eventLive\n            tags\n            episodeNumber\n            billingType\n            tier\n            seoTitle\n            slug\n            webUrl\n            rating\n            tvShow {\n              id\n              title\n              originalTitle\n              assetSubType\n            }\n            contentPartner {\n              id\n              name\n              image {\n                rectangleDarkLogo\n                rectangleWhiteLogo\n                circleDarkLogo\n                circleWhiteLogo\n              }\n            }\n          }\n          ... on Movie {\n            id\n            title\n            originalTitle\n            duration\n            contentOwner\n            businessType\n            genres {\n              id\n              value\n            }\n            languages\n            description\n            assetType\n            assetSubType\n            releaseDate\n            viewCount {\n              formattedCount\n              count\n            }\n            image {\n              list\n              cover\n              sticker\n              appCover\n              svodCover\n              verticalBanner\n              appSvodCover\n            }\n            actors\n            ageRating\n            audioLanguages\n            subtitleLanguages\n            eventLive\n            tags\n            billingType\n            tier\n            playDate\n            seoTitle\n            slug\n            webUrl\n            rating\n            relatedContentIds {\n              id\n            }\n            contentPartner {\n              id\n              name\n              image {\n                rectangleDarkLogo\n                rectangleWhiteLogo\n                circleDarkLogo\n                circleWhiteLogo\n              }\n            }\n          }\n        }\n        totalResults\n      }\n      page\n      size\n      totalResults\n    }\n  }\n",
                "variables": {
                    "id": id,
                    "filter": {
                        "page": page,
                        "translation": "en",
                        "languages": "en,hi,mr",
                        "country": "IN",
                        "limit": 20,
                        "itemLimit": 10,
                    },
                },
            }
        )
        resp = self.post(URLS.get("PAGE"), data=payload)
        return deep_get(resp, "data.collection")

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
