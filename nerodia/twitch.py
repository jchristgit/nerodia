import asyncio
import aiohttp
from collections import namedtuple
from typing import Dict, Optional, List, NamedTuple, Union


BASE_URL = "https://api.twitch.tv/helix"
USER_ENDPOINT = BASE_URL + "/users"
STREAM_ENDPOINT = BASE_URL + "/streams"


class TwitchStream(NamedTuple):
    id: int
    user_id: int
    thumbnail_url: str
    title: str
    viewer_count: int

    @classmethod
    def from_data(cls, data):
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            thumbnail_url=data["thumbnail_url"],
            title=data["title"],
            viewer_count=data["viewer_count"],
        )


TwitchUser = namedtuple("TwitchUser", "id name profile_image_url offline_image_url")


class TwitchClient:

    def __init__(self, client_id: str):
        self._cs = aiohttp.ClientSession(
            loop=asyncio.get_event_loop(),
            raise_for_status=True,
            headers={"Client-ID": client_id},
        )

    def __del__(self):
        if self._cs is not None:
            self._cs.close()

    async def _get(self, url: str, **kwargs) -> Dict[str, Union[Dict, List]]:
        async with self._cs.get(url, **kwargs) as resp:
            return await resp.json()

    async def _post(self, url: str, **kwargs) -> int:
        async with self._cs.post(url, **kwargs) as resp:
            return resp.status

    async def get_user(self, user_name: str) -> Optional[TwitchUser]:
        """Obtain information about a single Twitch user.

        Arguments:
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

    async def get_users(self, *user_names: str) -> List[TwitchUser]:
        """Obtain a list of Twitch users with the specified names.

        Arguments:
            user_names (str):
                The list of usernames whose Twitch user
                information should be returned.

        Returns:
            List[TwitchUser]:
                A list of `TwitchUser` instances for the given data.
                If a user could not be found, they will be omitted
                from the resulting List.
        """

        res = await self._get(USER_ENDPOINT + "?login=" + "&login=".join(user_names))

        return [
            TwitchUser(
                user["id"],
                user["login"],
                user["profile_image_url"],
                user["offline_image_url"],
            )
            for user in res["data"]
        ]

    async def get_streams(
        self, *stream_logins: str
    ) -> Dict[str, Optional[TwitchStream]]:
        """Obtain a mapping of given usernames to streams.

        Arguments:
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
            params = "&user_id=".join(user.id for user in users)
            res = await self._get(STREAM_ENDPOINT + "?user_id=" + params)
            streams = map(TwitchStream.from_data, res["data"])
            for user in users:
                result[user.name] = next(
                    (stream for stream in streams if stream.user_id == user.id), None
                )

        return result
