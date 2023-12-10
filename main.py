import itertools
import json
from requests import post, get
import os
from dotenv import load_dotenv
import pandas as pd
import base64
import time
import concurrent.futures
import numpy as np

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


# %% Functions
def get_token():
    """Returns authorization token from Spotify API"""

    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
    }

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    """Returns authorization header for get request"""

    return {"Authorization": "Bearer " + token}


def get_popularity(token, tracks_ids):
    ids_string = ",".join(tracks_ids)
    url = f"https://api.spotify.com/v1/tracks?ids={ids_string}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    popularity_indexes = [track["popularity"] for track in json_result["tracks"]]
    return popularity_indexes


auth_token = get_token()

# %%
df = pd.read_csv("data/tracks_features.csv")

ids = df['id']

# %%
start = time.time()
print(get_popularity(auth_token, ids[50:100]))
stop = time.time()
print(stop - start)

# %%

start = time.time()
popularity_list1 = [get_popularity(auth_token, ids[i:i + 50]) for i in range(0, 10001, 50)]
stop = time.time()
print(stop - start)

# %%
import asyncio
import aiohttp
from codetiming import Timer


async def task(name, work_queue):
    timer = Timer(text=f"Task {name} elapsed time: {{:.1f}}")
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            url = await work_queue.get()
            print(f"Task {name} getting URL: {url}")
            timer.start()
            async with session.get(url) as response:
                await response.text()
            timer.stop()


async def main():
    """
    This is the main entry point for the program
    """
    # Create the queue of work
    work_queue = asyncio.Queue()

    # Put some work in the queue
    for url in [
        "http://google.com",
        "http://yahoo.com",
        "http://linkedin.com",
        "http://apple.com",
        "http://microsoft.com",
        "http://facebook.com",
        "http://twitter.com",
    ]:
        await work_queue.put(url)

    # Run the tasks
    with Timer(text="\nTotal elapsed time: {:.1f}"):
        await asyncio.gather(
            asyncio.create_task(task("One", work_queue)),
            asyncio.create_task(task("Two", work_queue)),
        )


asyncio.run(main())
