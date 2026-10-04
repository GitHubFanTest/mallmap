# clean.py
import json

SRC = "all-malls.geojson"
OUT = "malls-clean.geojson"

data = json.load(open(SRC))
feats = data["features"]
print("start:", len(feats))

named = []
for f in feats:
    p = f["properties"]
    name = (p.get("name") or "").strip()
    if not name or name.lower() == "unnamed":
        name = "unnamed mall"
    p["name"] = name
    named.append(f)

kept = {}
dupes = 0
for f in named:
    p = f["properties"]
    lon, lat = f["geometry"]["coordinates"]
    key = p["name"].lower()
    match = None
    for k in kept.get(key, []):
        klon, klat = k["geometry"]["coordinates"]
        if abs(klon - lon) < 0.002 and abs(klat - lat) < 0.002:
            match = k
            break
    if match:
        dupes += 1
        for field in ("operator", "website"):
            if not match["properties"].get(field) and p.get(field):
                match["properties"][field] = p[field]
    else:
        kept.setdefault(key, []).append(f)

out = []
for group in kept.values():
    for f in group:
        lon, lat = f["geometry"]["coordinates"]
        f["geometry"]["coordinates"] = [round(lon, 5), round(lat, 5)]
        f["properties"] = {k: v for k, v in f["properties"].items() if v}
        out.append(f)

print("duplicates merged:", dupes)
print("final:", len(out))

with open(OUT, "w") as fh:
    json.dump({"type": "FeatureCollection", "features": out}, fh, separators=(",", ":"))
