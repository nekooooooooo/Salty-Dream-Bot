import json
import os
import dotenv
import aiohttp

dotenv.load_dotenv()

URL = os.getenv('URL')

async def show_progress():
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"{URL}/sdapi/v1/progress") as result:
            return result.json()
