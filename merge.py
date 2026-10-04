# merge_geo.py
import json
import sys

seen = {}
for path in sys.argv[1:]:
    for f in json.load(open(path))["features"]:
        seen[f["properties"]["id"]] = f

with open("all-malls.geojson", "w") as out:
    json.dump({"type": "FeatureCollection", "features": list(seen.values())}, out)
print("merged", len(seen), "malls")
