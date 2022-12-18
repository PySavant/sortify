import os
import dotenv
import logging

from spotify.oauth import SpotifyOAuth
from spotify.client import SpotifyClient


dotenv.load_dotenv()
logger = logging.getLogger("sortify")


class Sortify():

    id: str = os.getenv('SPOTIFY_CLIENT_ID')
    secret: str = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect: str = os.getenv('SPOTIFY_REDIRECT_URI')

    def __init__(self):
        self.auth = SpotifyClient(self)
