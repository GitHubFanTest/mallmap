# refresh.py
import json
import os
import time

import requests

URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {
    "User-Agent": "mallmap/1.0 (+https://bryce.is-a.dev/mallmap; https://github.com/GitHubFanTest/mallmap)",
    "Accept": "*/*",
}

tiles = {
    "africa": "-35,-20,38,52",
    "southamerica": "-56,-92,13,-34",
    "oceania": "-50,110,0,180",
    "europe-west": "35,-25,72,10",
    "europe-east": "35,10,72,45",
    "asia-west": "-11,25,40,60",
    "asia-south": "-11,60,40,100",
    "asia-east": "-11,100,55,150",
    "asia-north": "40,25,78,180",
    "na-west": "5,-170,84,-105",
    "na-east": "5,-105,84,-50",
}

os.makedirs("tiles", exist_ok=True)
START = time.time()
BUDGET = 4 * 3600


def get_tile(name, bbox):
    query = f'[out:json][timeout:180][maxsize:1073741824];nwr["shop"="mall"]({bbox});out center tags;'
    for attempt in range(6):
        url = URLS[attempt % len(URLS)]
        try:
            res = requests.post(url, data={"data": query}, headers=HEADERS, timeout=200)
            if res.ok:
                return res.json()["elements"]
            print(name, url, "got", res.status_code, flush=True)
        except Exception as e:
            print(name, url, "failed:", e, flush=True)
        time.sleep(min(30 * (attempt + 1), 150))
    return None


failed = []
for name, bbox in tiles.items():
    if time.time() - START > BUDGET:
        print("out of time, skipping", name, flush=True)
        failed.append(name)
        continue
    elements = get_tile(name, bbox)
    if elements is None:
        failed.append(name)
        print(name, "failed, keeping old copy", flush=True)
        continue
    with open(f"tiles/{name}.json", "w") as f:
        json.dump(elements, f)
    print(name, len(elements), "malls", flush=True)
    time.sleep(15)

print("failed tiles:", failed or "none", flush=True)
