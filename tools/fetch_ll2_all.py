#!/usr/bin/env python3
"""Download ALL past launches from Launch Library 2 (every provider) into data_raw/retrieved/ll2/all_<offset>.json.
Resumable; waits when the free API rate limit (HTTP 429) is hit."""
import json, os, re, sys, time, urllib.request, urllib.error
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(ROOT, "data_raw", "retrieved", "ll2")
os.makedirs(D, exist_ok=True)
off = 0
while True:
    f = os.path.join(D, f"all_{off}.json")
    if os.path.exists(f):
        d = json.load(open(f))
    else:
        url = f"https://ll.thespacedevs.com/2.2.0/launch/previous/?limit=100&offset={off}&format=json&mode=normal"
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "space-mission-dataset/1.0"}), timeout=90).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                m = re.search(r"(\d+) seconds", e.read().decode(errors="ignore"))
                w = int(m.group(1)) + 5 if m else 300
                print(f"429 at offset {off}; sleeping {w}s", flush=True); time.sleep(min(w, 3700)); continue
            raise
        d = json.loads(raw); open(f, "wb").write(raw); print("fetched", off, "of", d["count"], flush=True)
        time.sleep(2)
    if not d.get("next"): break
    off += 100
print("done", off)
