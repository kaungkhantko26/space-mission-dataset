#!/usr/bin/env python3
"""Download selected Artemis II PDS reference assets from official NASA PDS/NAIF hosts.

Default: downloads two small Orion locker environment CSVs and their PDS4 XML labels.
Optional --include-spice downloads the Artemis II NAIF meta-kernel and every kernel it lists.
That full SPICE set includes the DE430 planetary kernel (about 114 MB per NAIF index).
Run on a computer with internet access. No credentials are required for these listed PDS files.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import argparse, csv, hashlib, re, sys, time

OUT = Path(__file__).resolve().parents[1] / "downloaded_official_assets"
PDS_BASE = "https://pds-geosciences.wustl.edu/artemis2/urn-nasa-pds-artemis2_mission/data_orion_environment/"
SPICE_BASE = "https://naif.jpl.nasa.gov/pub/naif/pds/pds4/artemis2/artemis2_spice/"
ENV_FILES = [
    "art002_086-162546_111-205046_hobo1104_raw_v01.csv",
    "art002_086-162546_111-205046_hobo1104_raw_v01.xml",
    "art002_086-162926_111-203826_hobo1105_raw_v01.csv",
    "art002_086-162926_111-203826_hobo1105_raw_v01.xml",
]

def fetch(url: str, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "SpaceMissionResearchDataDownloader/1.0"})
    last_error = None
    for attempt in range(3):
        try:
            with urlopen(req, timeout=60) as response, destination.open("wb") as out:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if destination.stat().st_size == 0:
                raise RuntimeError("Downloaded empty file")
            digest = hashlib.sha256(destination.read_bytes()).hexdigest()
            return {"url": url, "local_path": str(destination.relative_to(OUT)), "status": "downloaded", "bytes": destination.stat().st_size, "sha256": digest, "error": ""}
        except (URLError, HTTPError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = str(exc)
            time.sleep(1 + attempt)
    return {"url": url, "local_path": str(destination.relative_to(OUT)), "status": "failed", "bytes": 0, "sha256": "", "error": last_error or "unknown error"}

def download_environment(records):
    for name in ENV_FILES:
        records.append(fetch(PDS_BASE + name, OUT / "artemis2_mission" / "data_orion_environment" / name))

def download_spice(records):
    mk_rel = "spice_kernels/mk/artemis2_v01.tm"
    mk_path = OUT / "artemis2_spice" / mk_rel
    rec = fetch(SPICE_BASE + mk_rel, mk_path)
    records.append(rec)
    if rec["status"] != "downloaded":
        print("Could not retrieve meta-kernel; skipping SPICE dependencies.", file=sys.stderr)
        return
    text = mk_path.read_text(encoding="utf-8", errors="replace")
    rels = sorted(set(re.findall(r"\$KERNELS/([^'\s]+)", text)))
    for rel in rels:
        url = SPICE_BASE + "spice_kernels/" + rel
        dest = OUT / "artemis2_spice" / "spice_kernels" / rel
        records.append(fetch(url, dest))
        # Fetch PDS4 label sibling where present; not every archive may expose one.
        if dest.suffix.lower() in {".bsp", ".bc", ".tf", ".ti", ".tpc", ".bpc", ".tls", ".tsc"}:
            label_url = url.rsplit(".", 1)[0] + ".xml"
            label_dest = dest.with_suffix(".xml")
            label_record = fetch(label_url, label_dest)
            if label_record["status"] == "failed" and "404" in label_record.get("error", ""):
                continue
            records.append(label_record)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-spice", action="store_true", help="Also download Artemis II NAIF SPICE meta-kernel and all referenced kernels (includes ~114 MB DE430).")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    download_environment(records)
    if args.include_spice:
        download_spice(records)
    manifest = OUT / "download_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "local_path", "status", "bytes", "sha256", "error"])
        w.writeheader(); w.writerows(records)
    failed = [r for r in records if r["status"] == "failed"]
    print(f"Download manifest: {manifest}")
    print(f"Downloaded: {sum(r['status']=='downloaded' for r in records)}; failed: {len(failed)}")
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
