"""
fetch_capitals.py
Fetch capitals & coordinates for:
 - region: Europe
 - subregion: South-Eastern Asia
 - subregion: Southern Asia

Writes UTF-8 CSV to: data/cities_capitals_europe_seasia.csv
"""

import csv
import os
import requests
from urllib.parse import quote

RESTCOUNTRIES_BASE = "https://restcountries.com/v3.1"
OUT_DIR = "data"
OUT_CSV = os.path.join(OUT_DIR, "cities_capitals_europe_seasia.csv")


def fetch_region(region_name):
    url = f"{RESTCOUNTRIES_BASE}/region/{quote(region_name)}"
    print(f"Fetching {url} ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_subregion(subregion_name):
    url = f"{RESTCOUNTRIES_BASE}/subregion/{quote(subregion_name)}"
    print(f"Fetching {url} ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_country_capital(item, region_label):
    country_name = item.get('name', {}).get('common') or ""
    capitals = item.get('capital') or []
    capital = capitals[0] if capitals else None

    cap_info = item.get('capitalInfo', {}) or {}
    latlon = cap_info.get('latlng')

    if not latlon:
        latlon = item.get('latlng')

    if isinstance(latlon, list) and len(latlon) >= 2:
        lat, lon = float(latlon[0]), float(latlon[1])
    else:
        lat, lon = None, None

    return {
        "country": country_name,
        "city": capital if capital else country_name,
        "lat": lat,
        "lon": lon,
        "region": region_label
    }


def ensure_outdir():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR, exist_ok=True)


def write_csv(rows, filename):
    cols = ["country", "city", "lat", "lon", "region"]
    ensure_outdir()
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            safe = {k: ("" if r.get(k) is None else r.get(k)) for k in cols}
            writer.writerow(safe)
    print(f"Wrote {len(rows)} rows to {filename}")


def main():
    europe = fetch_region("europe")
    se_asia = fetch_subregion("South-Eastern Asia")
    south_asia = fetch_subregion("Southern Asia")  
    rows = []
    seen = set()

    for item in europe:
        rec = extract_country_capital(item, "Europe")
        key = (rec['country'], rec['city'])
        if key not in seen:
            rows.append(rec); seen.add(key)

    for item in se_asia:
        rec = extract_country_capital(item, "SE_Asia")
        key = (rec['country'], rec['city'])
        if key not in seen:
            rows.append(rec); seen.add(key)

    for item in south_asia:
        rec = extract_country_capital(item, "South_Asia")
        key = (rec['country'], rec['city'])
        if key not in seen:
            rows.append(rec); seen.add(key)

    rows = sorted(rows, key=lambda r: (r['region'], r['country'] or ""))
    write_csv(rows, OUT_CSV)
    print("Done. Now run: python import_into_neo4j.py")


if __name__ == '__main__':
    main()
