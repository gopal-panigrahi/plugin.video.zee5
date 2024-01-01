# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.utils import update_query_params
from resources.lib.constants import DEFAULT_PARAMS, DEVICE_ID, URLS, url_constructor
from resources.lib.api import Zee5API
from resources.lib.builder import Builder
import urlquick
from codequick import Route, run, Script, Resolver, Listitem
from codequick.script import Settings
import random, string


@Route.register
def root(_):
    yield Listitem.search(Route.ref("/resources/lib/main:list_search"), url="search")
    yield from builder.build_menu()


@Route.register
def list_collection(_, **kwargs):
    if "id" in kwargs:
        page = api.get_page(kwargs.get("id"), kwargs.get("end") // 20)
        kwargs["total"] = page.get("totalResults")
        yield from builder.build_collection(page.get("rails"))
        yield from builder.build_next(**kwargs)
    else:
        return False


@Route.register
def list_search(_, **kwargs):
    if kwargs.get("search_query", False):
        keyword = kwargs.get("search_query")
        items = api.get_search_result(keyword)
        yield from builder.build_page(items)
    else:
        yield False


@Route.register
def list_page(_, **kwargs):
    if "id" in kwargs:
        page = api.get_page(kwargs.get("id"), kwargs.get("end") // 20)
        kwargs["total"] = page.get("totalResults")
        yield from builder.build_page(page.get("rails")[0].get("contents"))
        yield from builder.build_next(**kwargs)
    else:
        return False


@Route.register(redirect_single_item=True)
def list_seasons(_, **kwargs):
    if "item_id" in kwargs:
        url = f"tvshow/{kwargs.get('item_id')}"
        seasons = api.get_seasons(url)
        yield from builder.build_seasons(seasons, kwargs.get("item_id"))
    else:
        yield False


@Route.register
def list_episodes(_, **kwargs):
    if "season_id" in kwargs:
        page = kwargs.get("page", 1)
        key = "episode"
        if page == 1:
            url = f"tvshow/{kwargs.get('show_id')}"
            episodes = api.get_seasons(url)[0]
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
            url = update_query_params(url, queryParams)
            episodes = api.get_episodes(url)

        total_episodes = episodes.get("total_episodes")
        yield from builder.build_episodes(episodes.get(key), kwargs.get("show_id"))
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
        url = update_query_params(url, queryParams)
        if kwargs.get("mediatype") != "movie":
            url = update_query_params(url, {"show_id": kwargs.get("show_id")})
        key_details, video_details = api.get_video(url)
        stream_headers = api._get_play_headers()
        return builder.build_play(video_details, stream_headers, key_details)


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
