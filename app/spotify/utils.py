import logging

logger = logging.getLogger('sortify')

class BaseSortify():
    ''' Utility Class for Sortify Functions '''

    _library: str = 'https://api.spotify.com/v1/me/tracks?limit=50&offset={}'
    _artists: str = 'https://api.spotify.com/v1/artists?ids={}'
    _userid: str = 'https://api.spotify.com/v1/me'
    _create: str = 'https://api.spotify.com/v1/users/{}/playlists'
    _addsongs: str = 'https://api.spotify.com/v1/playlists/playlist/{}/tracks'

    file: str = '/home/savant/Desktop/sortify/app/data/library.json'

    @staticmethod
    def getLibrary(songs: list) -> []:
        logger.trace(f'Adding {len(songs)} songs to Library')

        def _build(song):
            return {
                'id': song['track']['id'],
                'artist': song['track']['artists'][0]['id']
            }

        return [_build(song) for song in songs]

    @staticmethod
    def _chunk(items: list, *, size: int = 50) -> []:
        chunks = [items[x:x+size] for x in range(0, len(items), size)]

        return chunks

    @staticmethod
    def getArtists(artists: list) -> []:
        logger.trace(f'Sorting {len(artists)} artists')

        def _build(artist):
            return {
                'id': artist['id'],
                'genres': artist['genres']
            }

        return [_build(artist) for artist in artists]

    @staticmethod
    def getURIs(songs: list) -> []:
        logger.trace('Generating Spotify URIs')

        def _build(id):
            return f"spotify:track:{id}"

        return [_build(id) for id in songs]
