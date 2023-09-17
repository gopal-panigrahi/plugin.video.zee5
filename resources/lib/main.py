# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.utils import updateQueryParams
from resources.lib.constants import DEFAULT_PARAMS, DEVICE_ID, URLS, url_constructor
from resources.lib.api import Zee5API
from resources.lib.builder import Builder
import urlquick
from codequick import Route, run, Script, Resolver, Listitem
from codequick.script import Settings
import random, string


@Route.register
def root(_):
    yield from builder.buildMenu()


@Route.register
def list_collection(_, **kwargs):
    if "id" in kwargs:
        page = api.getPage(kwargs.get("id"), kwargs.get("end") // 20)
        kwargs["total"] = page.get("totalResults")
        yield from builder.buildCollection(page.get("rails"))
        yield from builder.buildNext(**kwargs)
    else:
        return False


@Route.register
def list_page(_, **kwargs):
    if "id" in kwargs:
        page = api.getPage(kwargs.get("id"), kwargs.get("end") // 20)
        kwargs["total"] = page.get("totalResults")
        yield from builder.buildPage(page.get("rails")[0].get("contents"))
        yield from builder.buildNext(**kwargs)
    else:
        return False


@Route.register(redirect_single_item=True)
def list_seasons(_, **kwargs):
    if "item_id" in kwargs:
        url = f"tvshow/{kwargs.get('item_id')}"
        seasons = api.getSeasons(url)
        yield from builder.buildSeasons(seasons, kwargs.get("item_id"))
    else:
        yield False


@Route.register
def list_episodes(_, **kwargs):
    if "season_id" in kwargs:
        page = kwargs.get("page", 1)
        key = "episode"
        if page == 1:
            url = f"tvshow/{kwargs.get('show_id')}"
            episodes = api.getSeasons(url)[0]
            key = "episodes"
        else:
            url = url_constructor(f"tvshow/")
            queryParams = {
                "season_id": kwargs.get("season_id"),
                "page": page,
                "type": "episode",
                "on_air": "true",
                "asset_subtype": "tvshow",
                "limit": "25",
            }
            queryParams.update(DEFAULT_PARAMS)
            url = updateQueryParams(url, queryParams)
            episodes = api.getEpisodes(url)

        total_episodes = episodes.get("total_episodes")
        yield from builder.buildEpisodes(episodes.get(key), kwargs.get("show_id"))
        if page * 25 < total_episodes:
            yield Listitem.next_page(
                **{
                    "season_id": kwargs.get("season_id"),
                    "show_id": kwargs.get("show_id"),
                    "page": page + 1,
                }
            )
    else:
        yield False


@Route.register
def list_movies(_, **kwargs):
    page = kwargs.get("page", 1)
    movies = api.getMovies(page)
    yield from builder.buildMovies(movies)
    yield Listitem.next_page(**{"page": page + 1})


@Resolver.register
def play_video(_, **kwargs):
    if "mediatype" in kwargs:
        queryParams = {
            "content_id": kwargs.get("item_id"),
            "device_id": DEVICE_ID,
            "platform_name": "desktop_web",
            "translation": "en",
            "user_language": "en,hi,mr",
            "country": "IN",
            "state": "MH",
            "app_version": "2.51.32",
            "user_type": "guest",
            "check_parental_control": "false",
            "ppid": DEVICE_ID,
            "version": "12",
        }
        url = URLS.get("VIDEO")
        url = updateQueryParams(url, queryParams)
        if kwargs.get("mediatype") != "movie":
            url = updateQueryParams(url, {"show_id": kwargs.get("show_id")})
        key_details, video_details = api.getVideo(url)
        stream_headers = api._getPlayHeaders()
        return builder.buildPlay(video_details, stream_headers, key_details)


@Script.register
def cleanup(_):
    urlquick.cache_cleanup(-1)
    Script.notify("Cache Cleaned", "")


@Script.register
def generate_deviceid(_):
    x = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    device_id = f"{x}000000000000"
    Settings().__setitem__("device_id", device_id)


api = Zee5API()
builder = Builder()
