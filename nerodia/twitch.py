import asyncio
import aiohttp

from .config import TWITCH_CFG


BASE_URL = 'https://api.twitch.tv/helix'
USER_ENDPOINT = BASE_URL + '/users'
STREAM_TOPIC = BASE_URL + '/streams'
WEBHOOK_ENDPOINT = BASE_URL + '/webhooks/hub'


class TwitchClient:
    def __init__(self, client_id: str):
        self._cs = aiohttp.ClientSession(
            loop=asyncio.get_event_loop(),
            raise_for_status=True,
            headers={'Client-ID': client_id}
        )

    def __del__(self):
        if self._cs is not None:
            self._cs.close()

    async def _get(self, url, **kwargs):
        async with self._cs.get(url, **kwargs) as resp:
            return await resp.json()

    async def _post(self, url, **kwargs):
        async with self._cs.post(url, **kwargs) as resp:
            return resp.status

    async def _update_event_subscription(self, hub_topic, sub=True, **kwargs):
        return await self._post(
            WEBHOOK_ENDPOINT,
            data={
                'hub.topic': hub_topic,
                'hub.mode': 'subscribe' if sub else 'unsubscribe',
                'hub.callback': TWITCH_CFG['webhook_callback_url']
            }
        )

    async def sub_stream(self, user_id):
        return await self._update_event_subscription(
            f'{STREAM_TOPIC}?user_id={user_id}'
        )

    async def unsub_stream(self, user_id):
        return await self._update_event_subscription(
            f'{STREAM_TOPIC}?user_id={user_id}',
            sub=False
        )

    async def get_user(self, user_name: str):
        res = await self._get(
            USER_ENDPOINT,
            params={'login': user_name}
        )
        return res['data'][0] if res['data'] else None
