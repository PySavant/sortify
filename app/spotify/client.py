import os
import aiohttp
import asyncio
import logging

logger = logging.getLogger("sortify.client")


class SpotifyClient():
    '''' Allows Client Authorized Requests to Spotify Web API '''

    token: str = None

    url: str = 'https://accounts.spotify.com/api/token'

    def __init__(self, app):
        self.app = app

        asyncio.run(self.authenticate())

    async def authenticate(self):
        payload = {
            'client_id': self.app.id,
            'client_secret': self.app.secret,
            'grant_type': 'client_credentials'
        }

        logger.info('Requesting Client Access Token')

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=payload) as request:
                response = await request.json()

        try:
            self.token = f'Bearer {response["access_token"]}'

        except KeyError:
            logger.fatal('Unexpected Error -> Invalid Response Key: "access_token"')

        else:
            logger.info('Successfully Retrieved Client Access Token')
