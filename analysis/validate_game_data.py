
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "game_data"

for name in ["earth", "mars"]:
    path = DATA_DIR / f"{name}_vectors.json"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data["records"]

    assert len(records) == 260, f"{name}: Unexpected record count"

    required = [
        "jdTdb",
        "date",
        "positionAu",
        "velocityAuPerDay"
    ]

    for record in records:
        for key in required:
            assert key in record, f"{name}: Missing {key}"

        for group in ["positionAu", "velocityAuPerDay"]:
            for axis in ["x", "y", "z"]:
                value = record[group][axis]
                assert isinstance(value, (int, float)), (
                    f"{name}: Invalid {group}.{axis}"
                )

    print(f"{name.upper()}: PASS")
    print(f"Records: {len(records)}")
    print(f"First date: {records[0]['date']}")
    print(f"Last date: {records[-1]['date']}")
    print("-" * 40)

print("ALL DATA VALIDATION PASSED")
