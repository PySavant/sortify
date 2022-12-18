import os
import json
import dotenv
import aiohttp
import asyncio


from .spotify.oauth import SpotifyOAuth
from .spotify.client import SpotifyClient
from .spotify.utils import BaseSortify


dotenv.load_dotenv()



class Sortify(BaseSortify):

    id: str = os.getenv('SPOTIFY_CLIENT_ID')
    secret: str = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect: str = os.getenv('SPOTIFY_REDIRECT_URI')

    def __init__(self, logger):
        self.auth = SpotifyClient(self)
        self.oauth = SpotifyOAuth(self)

        self.logger = logger
        self.library = []

    # Operations

    def _artists(self) -> []:
        self.logger.debug('Loading Local Library')
        with open(self.file, 'r') as file:
            songs = json.load(file)

        self.logger.trace('Identifying Unique Artists')
        artists = list( {song['aritst'] for song in songs} )

        self.logger.info(f'Found {len(_artists)} unique artists')

        return artists

    async def _download(self, auth: dict):
        offset = 0
        url = self._library

        async with aiohttp.ClientSession(headers=auth) as session:
            async with session.get(url.format(offset)) as request:
                response = await request.json()
                total = response["total"]

            self.logger.info(f'Found {total} songs available for download')

            while len(self.library) < total:
                offset += 50
                self.library += self.getLibrary(response['items'])

                progress = (len(self.library)/total) * 100
                remaining = (total - len(self.library)) / 6000

                self.logger.debug(f'Progress: {progress:2.2f}% - {remaining:2.2f} minutes left')

                await asyncio.sleep(0.5)

                async with session.get(url.format(offset)) as request:
                    response = await request.json()

    async def _genres(self):
        _artists = self._artists()

        artists = {}

        async with aiohttp.ClientSession(headers=header) as session:
            chunks = [','.join(chunk) for chunk in self._chunk(_artists)]

            for chunk in chunks:
                async with session.get(url.format(chunk)) as request:
                    response = await request.json()

                for artist in super().getArtists(response['artists']):
                    artists.update(artist)

                progress = len(artists)/len(_artists) * 100
                remaining = (len(_artists) - len(artists)) / 6000

                self.logger.debug(f'Progress {progress:2.2f}% - {remaining:2.2f} minutes left')

                await asyncio.sleep(0.5)

        return artists

    async def _playlist(self, name: str, *, songs: []):
        header = {
            'Authorization': self.oauth.token,
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession(headers=header) as session:
            if not self.userID:
                self.logger.debug('Fetching User ID')
                async with session.get(self.userid) as request:
                    response = await request.json()

                self.userID = response['id']

            url = self._create
            playlist = {
                'name': name,
            }

            self.logger.debug(f'Creating Playlist: {name}')
            async with session.post(url.format(self.userID), data=playlist) as request:
                response = await request.json()

            playlistid = response['id']

            url = self._addsongs
            songs = self.getURIs(songs)
            chunks = self._chunk(songs, size=100)
            size = 0

            for chunk in chunks:
                size += len(chunk)
                data = {"uris": chunk}

                self.logger.trace(f'Adding {len(chunk)} songs to playlist')
                await session.post(url.format(playlistid), data=data)

                progress = (size / len(songs)) * 100
                remaining = (len(songs) - size) / 200

                self.logger.debug(f'Progress {progress:2.2f}% - {remaining:2.2f} seconds left')

                await asyncio.sleep(0.5)

            self.logger.info('Playlist Complete')



    # Controlling

    async def download_library(self):
        header = {
            'Authorization': self.oauth.token,
            'Content-Type': 'application/json'
        }

        self.logger.info('Accessing Liked Songs Library')
        await self._download(header)

        self.logger.info(f'Download Complete: Saving {len(self.library)} songs to Local File System')

        with open(self.file, 'w+') as file:
            json.dump(self.library, file, indent=4)

        self.logger.info('Save Complete')

    async def update_library(self):
        header = {
            'Authorization': self.auth.token,
            'Content-Type': 'application/json'
        }

        self.logger.info('Collecting Genre Information')
        artists = await self._genres()

        self.logger.info('Updating Library')

        for song in self.library:
            song['genres'] = artists[song['artist']]

        with open(self.file, 'w+') as file:
            json.dump(self.library, file, indent=4)

        self.logger.info('Update Complete')

    async def generate(self):
        genres = {genre: [] for genre in {song['genres'] for song in self.library}}
        self.logger.debug(f'Identified {len(genres)} unique genres')

        self.logger.info('Building Playlists')

        for song in self.library:
            for genre in song['genres']:
                genres[genre].append(song['id'])

        self.logger.info('Creating Inclusive Playlists')

        for genre, playlist in genres.items():
            if len(playlist) >= 1000:
                await self._playlist(f'AI {genre}', songs=playlist)

        self.logger.info('Inclusive Playlists Complete')

        self.logger.info('Creating Specific Playlists')

        for genre, playlist in genres.items():
            if len(playlist) > 250 and len(playlist) < 1000:
                await self._playlist(genre, songs=playlist)

        return
