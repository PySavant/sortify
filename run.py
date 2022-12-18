import os
import json
import asyncio

from app import Sortify
from app.logger import Config



logger = Config.setLogger()
app = Sortify(logger)


async def main():
    await app.download_library()
    await app.update_library()

    with open(app.file, 'r') as file:
        app.library = json.load(file)

    await app.generate()


if __name__ == '__main__':
    asyncio.run(main())
