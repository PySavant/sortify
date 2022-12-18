import os
import time
import base64
import aiohttp
import asyncio
import logging

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


logger = logging.getLogger("sortify.oauth")


class SpotifyOAuth():
    ''' Allows User OAuth 2.0 Requests to Spotify Web API '''

    token: str = None

    auth_url: str = 'https://accounts.spotify.com/authorize?{}'
    token_url: str = 'https://accounts.spotify.com/api/token'


    def __init__(self, app):
        self.app = app

        asyncio.run(self.authenticate())

    @staticmethod
    def getAuth(app) -> str:
        logger.trace('Building Base64 Encoded Authorization String')

        format = f'{app.id}:{app.secret}'
        format_ascii = format.encode("ascii")

        return base64.urlsafe_b64encode(format_ascii)

    @staticmethod
    def login(url: str) -> str:
        ''' Logs into Spotify User Account and Authorizes Sortify '''

        username = input('Please Enter your Spotify Email or Username: ')
        password = input('Please Enter your Spotify Password: ')

        logger.trace('Opening Firefox Window')
        browser = webdriver.Firefox()

        logger.trace('Accessing Spotify Connect URL')
        browser.get('https://accounts.spotify.com/en/login')

        logger.trace('Locating Login Field: username')
        user = browser.find_element(By.XPATH, '//*[@id="login-username"]')

        logger.trace('Sending username')
        user.send_keys(username)

        logger.trace('Locating Login Field: password')
        pword = browser.find_element(By.XPATH, '//*[@id="login-password"]')

        logger.trace('Sending password')
        pword.send_keys(password)

        logger.trace('Locating Login Button')
        login = browser.find_element(By.XPATH, '//*[@id="login-button"]/div[1]/p')


        logger.trace('Clicking Login Button')
        login.click()

        time.sleep(5)
        logger.trace('Accessing Spotify Connect URL')
        try:
            browser.get(url)

            try:
                logger.trace('Locating Authorization Button')
                authorize = browser.find_element(By.XPATH, '/html/body/div/div/div[2]/div/div/div[3]/button')

            except Exception as e:
                logger.warning('No Button Found: Assuming Prior Authorization')
                url = browser.current_url

            else:
                logger.trace('Clicking Authorization Button')
                authorize.click()
                url = browser.current_url

        except WebDriverException as e:
            url = str(e).split('code%3D')[1].split('&c')[0]

        return url

    def getAuthURL(self) -> str:
        ''' Builds the Request URL for a User Authorization Code '''

        scope = 'user-library-read playlist-modify-private'

        args = {
            'client_id': self.app.id,
            'response_type': 'code',
            'redirect_uri': self.app.redirect,
            'scope': scope
        }

        query = '&'.join(f'{key}={value}' for key, value in args.items())

        return self.auth_url.format(query)

    async def getToken(self, *, code: str, type: str):
        ''' Exchanges a User Authorization Code for a User Access Token '''

        logger.trace(f'Requesting a {type} token: {code}')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.getAuth(self.app).decode("ascii")}'
        }

        if type == 'authorization':
            data = {
                'code': code,
                'redirect_uri': self.app.redirect,
                'grant_type': 'authorization_code'
            }
        elif type == 'refresh':
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': code
            }


        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.token_url, data=data) as request:
                response = await request.json()

        try:
            self.token = f'Bearer {response["access_token"]}'

        except KeyError:
            logger.fatal('Unexpected Error -> Invalid Response Key: "access_token"')

        else:
            logger.debug(f'Successfully Retrieved {type.title()} Token')
            return self.token


    async def authenticate(self, *, refresh: str = None) -> None:
        ''' Guides the User through connecting Sortify to their Spotify Account '''

        if not refresh:
            logger.trace('Building Spotify App Authorization URL')
            url = self.getAuthURL()

            logger.info('Authorizing Sortify to Access User Spotify Account')
            redirect = self.login(url)
            logger.trace('Ensuring a Successful Authorization Response')

            try:
                assert 'error' not in redirect
            except AssertionError:
                logger.fatal('Error: Inccorect Authorization Response')
            else:
                if 'code' in redirect:
                    logger.debug('Retrieving User Authorization Code')
                    code = redirect.split('?')[1].split('=')[1]
                else:
                    code = redirect

            logger.debug('Exchanging Auth Code for Access Token')
            token = await self.getToken(code=code, type='authorization')

        else:
            token = await self.getToken(code=refresh, type='refresh')

        if token:
            logger.info('Authorization Successful')

        return
