
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "game_data"
OUTPUT_DIR.mkdir(exist_ok=True)

DATASETS = {
    "earth": ROOT / "data_raw/solar_system/earth/earth_vectors.csv",
    "mars": ROOT / "data_raw/solar_system/mars/mars_vectors.csv",
}

def convert_to_json(name, csv_path):
    records = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            record = {
                "jdTdb": float(row["JD_TDB"]),
                "date": row["Calendar_Date_TDB"],
                "positionAu": {
                    "x": float(row["X_AU"]),
                    "y": float(row["Y_AU"]),
                    "z": float(row["Z_AU"])
                },
                "velocityAuPerDay": {
                    "x": float(row["VX_AU_per_day"]),
                    "y": float(row["VY_AU_per_day"]),
                    "z": float(row["VZ_AU_per_day"])
                }
            }
            records.append(record)

    output = {
        "metadata": {
            "body": name.capitalize(),
            "source": "NASA JPL Horizons",
            "recordCount": len(records),
            "positionUnit": "AU",
            "velocityUnit": "AU/day",
            "timeScale": "TDB"
        },
        "records": records
    }

    output_path = OUTPUT_DIR / f"{name}_vectors.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(f"{name.capitalize()}: {len(records)} records exported")
    print(f"Saved: {output_path}")

for name, csv_path in DATASETS.items():
    if not csv_path.exists():
        print(f"ERROR: Missing file: {csv_path}")
        continue

    convert_to_json(name, csv_path)

print("\nExport completed.")
