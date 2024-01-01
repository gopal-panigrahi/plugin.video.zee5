from __future__ import unicode_literals
from resources.lib.utils import update_query_params, deep_get
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
        self.token = self._get_token()
        self.session.headers.update(
            {"x-access-token": self.token, "Referer": "https://www.zee5.com/"}
        )

    def _get_token(self):
        url = "https://www.zee5.com/"
        resp = urlquick.get(url, headers=BASE_HEADERS)
        token = ""
        for t in re.findall(
            '"gwapiPlatformToken":"([^"]*)"', resp.content.decode("utf-8")
        ):
            if t != "":
                token = t
        return token

    def get_page(self, id, page):
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
                        "itemLimit": 5,
                    },
                },
            }
        )
        resp = self.post(URLS.get("PAGE"), data=payload)
        return deep_get(resp, "data.collection")

    def get_search_result(self, keyword):
        payload = json.dumps(
            {
                "query": "\nquery ($searchQueryInput: SearchQueryInput!) {\n    searchResults(searchQueryInput: $searchQueryInput) {\n      __typename\n      totalPages\n      currentPageIndex\n      totalResultsCount\n      currentResultsCount\n      limit\n      version\n      queryId\n      results {\n        title\n        duration\n        businessType\n        originalTitle\n        assetSubType\n        isIndiaImageEnabled\n        releaseDate\n        contentType\n        primaryGenre\n        audioLanguages\n        id\n        billingType\n        listImage\n        coverImage\n        imageUrl\n        subtitleLanguages\n        image {\n          listClean\n          square\n          appCover\n          tvCover\n          cover\n          list\n          portraitClean\n          portrait\n        }\n        genre {\n          id\n          value\n        }\n        actors\n        tvShow {\n          id\n          title\n          originalTitle\n          assetSubType\n        }\n      }\n    }\n  }\n",
                "variables": {
                    "searchQueryInput": {
                        "query": keyword,
                        "limit": 24,
                        "page": 0,
                        "country": "IN",
                        "filters": {},
                        "languages": "en,hi,mr",
                        "translation": "en",
                    },
                },
            }
        )
        resp = self.post(URLS.get("PAGE"), data=payload)
        return deep_get(resp, "data.searchResults.results")

    def get_collection(self, url):
        resp = self.get(url)
        collection = resp and resp.get("buckets")[0].get("items")
        total = resp and resp.get("total")
        return collection, total

    def get_seasons(self, url):
        url = url_constructor(url)
        url = update_query_params(url, {"translation": "en", "country": "IN"})
        resp = self.get(url)
        return resp.get("seasons")

    def get_episodes(self, url):
        url = url_constructor(url)
        episodes = self.get(url)
        return episodes

    def get_video(self, url):
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

        response = self.raw_post(url, headers, payload)

        return response.get("keyOsDetails"), response.get("assetDetails")

    def raw_post(self, url, headers, payload):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 401:
                Script.notify("Login Error", "Please login to continue")
            return response.json()
        except Exception as e:
            return self._handleError(e, url, "post")

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

    def _get_play_headers(self):
        stream_headers = self.session.headers
        return stream_headers
