# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.utils import get_images, callback_urls, deep_get, isPremium
from resources.lib.constants import MAIN_MENU
from codequick import Listitem, Resolver, Route
import inputstreamhelper
from urllib.parse import urlencode


class Builder:
    def buildMenu(self):
        for item_name, id, image in MAIN_MENU:
            item_data = {
                "callback": Route.ref("/resources/lib/main:list_collection"),
                "label": item_name,
                "params": {"id": id, "start": 0, "end": 20},
            }
            item = Listitem.from_dict(**item_data)
            item.art.local_thumb(image)
            yield item

    def buildCollection(self, items):
        for each in items:
            if each.get("title") and "Banner" not in each.get("title"):
                thumb, fanart = get_images(each.get("contents")[0])
                item_data = {
                    "callback": Route.ref("/resources/lib/main:list_page"),
                    "label": each.get("title"),
                    "art": {"thumb": thumb, "fanart": fanart},
                    "params": {"id": each.get("id"), "start": 0, "end": 20},
                }
                yield Listitem.from_dict(**item_data)

    def buildPage(self, items):
        for each in items:
            premium = isPremium(each)
            thumb, fanart = get_images(each)
            item_data = {
                "callback": callback_urls.get(each.get("assetSubType")),
                "label": f'{each.get("title")} {premium}',
                "art": {"thumb": thumb, "fanart": fanart},
                "info": {
                    "genre": [genre for _, genre in each.get("genre", [])],
                    "mpaa": each.get("ageRating"),
                    "plot": each.get("description"),
                    "mediatype": each.get("assetSubType"),
                    "castandrole": [
                        castandrole.split(":") for castandrole in each.get("actors", [])
                    ],
                },
                "params": {
                    "mediatype": each.get("assetSubType"),
                    "item_id": each.get("id"),
                    "show_id": deep_get(each, "tvShow.id"),
                    "start": 0,
                    "end": 20,
                },
            }
            yield Listitem.from_dict(**item_data)

    def buildSeasons(self, seasons, show_id):
        for each in seasons[::-1]:
            item_data = {
                "callback": Route.ref("/resources/lib/main:list_episodes"),
                "label": each.get("title"),
                "art": {
                    "thumb": "",
                    "fanart": "",
                },
                "params": {"season_id": each.get("id"), "show_id": show_id},
            }
            item = Listitem.from_dict(**item_data)
            item.art.local_thumb("season.png")
            yield item

    def buildNext(self, **kwargs):
        if kwargs.get("end") < kwargs.get("total"):
            kwargs["start"] += 20
            kwargs["end"] += 20
            yield Listitem().next_page(**kwargs)

    def buildEpisodes(self, episodes, show_id):
        for each in episodes:
            if each.get("business_type").split("_")[0] not in ["premium"]:
                thumb, fanart = get_images(each)
                item_data = {
                    "callback": Resolver.ref("/resources/lib/main:play_video"),
                    "label": f"Ep {each.get('episode_number')}. {each.get('title')}",
                    "art": {
                        "thumb": fanart,
                    },
                    "info": {
                        "mpaa": each.get("age_rating"),
                        "genre": [genre for _, genre in each.get("genre", [])],
                        "plot": each.get("description"),
                        "plotoutline": each.get("description"),
                        "episode": each.get("episode_number"),
                        "duration": each.get("duration"),
                        "castandrole": [
                            castandrole.split(":") for castandrole in each.get("actors")
                        ],
                        "season": each.get("season_details").get("index"),
                        "mediatype": each.get("asset_subtype"),
                    },
                    "params": {
                        "mediatype": each.get("asset_subtype"),
                        "item_id": each.get("id"),
                        "show_id": show_id,
                    },
                }
                yield Listitem.from_dict(**item_data)

    def buildPlay(self, video_details, stream_headers, key_details):
        video_urls = video_details.get("video_url")
        license_key = "|%s&Content-Type=application/octet-stream|R{SSM}|" % urlencode(
            stream_headers
        )

        if key_details.get("hls_token", None) is not None:
            manifest_type, playback_url = "hls", key_details.get("hls_token")
        elif video_details.get("hls_url", None) is not None:
            manifest_type, playback_url = "hls", video_details.get("hls_url")
        elif "mpd" in video_urls:
            manifest_type, playback_url = "mpd", video_urls.get("mpd")
            license_key = "https://spapi.zee5.com/widevine/getLicense" + license_key
        else:
            return False

        is_helper = inputstreamhelper.Helper("mpd", drm="com.widevine.alpha")
        stream_headers.update(
            {
                "customdata": key_details.get("sdrm"),
                "nl": key_details.get("nl"),
            }
        )
        if is_helper.check_inputstream():
            item_data = {
                "callback": playback_url,
                "label": video_details.get("title"),
                "properties": {
                    "IsPlayable": True,
                    "inputstream": is_helper.inputstream_addon,
                    "inputstream.adaptive.manifest_type": manifest_type,
                    "inputstream.adaptive.license_type": "com.widevine.alpha",
                    "inputstream.adaptive.stream_headers": urlencode(stream_headers),
                    "inputstream.adaptive.license_key": license_key,
                },
                "subtitles": video_details.get("vtt_thumbnail_url"),
            }
            return Listitem(content_type="video").from_dict(**item_data)
