import asyncio
from datetime import timedelta
from typing import Dict, Optional, List, NamedTuple, Mapping, Union

import aiohttp

from .decorators import timed_async_cache


BASE_URL = "https://api.twitch.tv/helix"
USER_ENDPOINT = BASE_URL + "/users"
STREAM_ENDPOINT = BASE_URL + "/streams"
JSON = Union[str, int, float, bool, None, Mapping[str, "JSON"], List["JSON"]]


class TwitchStream(NamedTuple):
    id: int
    user_id: int
    thumbnail_url: str
    title: str

    @classmethod
    def from_data(cls, data: JSON):
        """Create a new `TwitchStream` based on data returned by the `/streams` endpoint.

        Args:
            data (JSON):
                The data that should be used to populate this
                `TwitchStream` instance, as returned by the API.
        """

        def build_thumbnail_url(url: str) -> str:
            return url.replace('{width}', '1600').replace('{height}', '900')

        return cls(
            id=int(data["id"]),
            user_id=int(data["user_id"]),
            thumbnail_url=build_thumbnail_url(data["thumbnail_url"]),
            title=data["title"],
        )


class TwitchUser(NamedTuple):
    id: int
    name: str
    profile_image_url: str
    offline_image_url: str

    @classmethod
    def from_data(cls, data: JSON):
        """Create a new `TwitchUser` based on data returned by the `/users` endpoint.

        Args:
            data (JSON):
                The data that should be used to populate this
                `TwitchUser` instance, as returned by the API.
        """

        return cls(
            id=int(data["id"]),
            name=data["login"],
            profile_image_url=data["profile_image_url"],
            offline_image_url=data["offline_image_url"],
        )


class TwitchClient:
    """An asynchronous Twitch API client implementation.

    Manages its own `aiohttp.ClientSession` which is
    automatically closed once the client is garbage collected.
    """

    def __init__(self, client_id: str):
        """Create a new `TwitchClient` instance.

        Args:
            client_id (str):
                The client ID of the Twitch developer
                application to use for all requests.
                You can register an application here:
                `https://dev.twitch.tv/dashboard/apps`
        """

        self._cs = aiohttp.ClientSession(
            loop=asyncio.get_event_loop(),
            raise_for_status=True,
            headers={"Client-ID": client_id},
        )

    def __del__(self):
        """Close the `aiohttp.ClientSession` to prevent any warnings."""

        if self._cs is not None:
            self._cs.close()

    async def _get(self, url: str, **kwargs) -> JSON:
        """Execute HTTP GET.

        Args:
            url (str):
                The URL which should be requested.
            **kwargs:
                Any additional keyword arguments are
                directly passed to `aiohttp.ClientSession.get`.

        Returns:
            JSON:
                The JSON response returned by the website,
                as a parsed Python object.
        """

        async with self._cs.get(url, **kwargs) as resp:
            return await resp.json()

    async def _post(self, url: str, **kwargs) -> int:
        """Execute HTTP POST.

        Args:
            url (str):
                The URL which should be requested.
            **kwargs:
                Any additional keyword arguments are
                directly passed to `aiohttp.ClientSession.get`.

        Returns:
            int:
                The status code returned by the website.
        """

        async with self._cs.post(url, **kwargs) as resp:
            return resp.status

    async def get_user(self, user_name: str) -> Optional[TwitchUser]:
        """Obtain information about a single Twitch user.

        Args:
            user_name (str):
                The username for which Twitch user information should be returned.

        Returns:
            Optional[TwitchUser]:
                A populated instance of `TwitchUser` if the
                given username could be found, or `None` otherwise.
        """

        user_list = await self.get_users(user_name)
        if not user_list:
            return None
        return user_list[0]

    @timed_async_cache(expire_after=timedelta(hours=6))
    async def get_users(self, *user_names: str) -> List[TwitchUser]:
        """Obtain a list of Twitch users with the specified names.

        Args:
            user_names (str):
                The list of usernames whose Twitch user
                information should be returned.

        Returns:
            List[TwitchUser]:
                A list of `TwitchUser` instances for the given data.
                If a user could not be found, they will be omitted
                from the resulting List.

        Notes:
            This function's result for a specific set of
            arguments is cached for at least 6 hours.
        """

        res = await self._get(USER_ENDPOINT + "?login=" + "&login=".join(user_names))

        return [TwitchUser.from_data(user_data) for user_data in res["data"]]

    async def get_streams(
        self, *stream_logins: str
    ) -> Dict[str, Optional[TwitchStream]]:
        """Obtain a mapping of given usernames to streams.

        Args:
            stream_logins (str):
                An argument list of usernames for which stream
                should be obtained. This method assumes that
                every specified login is a valid, existing user.

        Returns:
            Dict[str, Optional[TwitchStream]]:
                Maps given usernames to `TwitchStream` instances.
                If the given user is streaming, the value represents
                information about the stream. If the stream is offline,
                this will be set to `None` instead.
        """

        result = {}
        login_chunks = (
            stream_logins[n:n + 100] for n in range(0, len(stream_logins), 100)
        )

        for login_chunk in login_chunks:
            users = await self.get_users(*login_chunk)
            params = "&user_id=".join(str(user.id) for user in users)
            res = await self._get(STREAM_ENDPOINT + "?user_id=" + params)
            streams = [
                TwitchStream.from_data(stream_data) for stream_data in res["data"]
            ]
            for user in users:
                result[user.name] = next(
                    (stream for stream in streams if stream.user_id == user.id), None
                )

        return result
