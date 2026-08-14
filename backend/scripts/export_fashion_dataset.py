import os
import sys
import json
import csv

# Ensure backend root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.wardrobe import WardrobeItem

def export_dataset(output_json: str = "fashion_dataset.json", output_csv: str = "fashion_dataset.csv"):
    """
    Exports wardrobe dataset containing image paths, AI predictions,
    and user-confirmed corrections to JSON and CSV formats.
    """
    db: Session = SessionLocal()
    try:
        items = db.query(WardrobeItem).all()
        dataset = []

        for item in items:
            record = {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "primary_color": item.attributes.primary_color if item.attributes else "white",
                "image_url": item.image_url,
                "style": item.attributes.style if item.attributes else "casual",
                "formality": item.attributes.formality if item.attributes else 3,
                "material": item.attributes.material if item.attributes else "cotton",
                "pattern": item.attributes.pattern if item.attributes else "solid",
                "fit": item.attributes.fit if item.attributes else "regular",
                "seasons": item.attributes.seasons if item.attributes else ["summer"],
                "occasions": item.attributes.occasions if item.attributes else ["casual"]
            }
            dataset.append(record)

        # Write JSON
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2)
        print(f"Exported {len(dataset)} items to {output_json}")

        # Write CSV
        if dataset:
            headers = list(dataset[0].keys())
            with open(output_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in dataset:
                    # serialize lists to strings for CSV
                    row_csv = row.copy()
                    if isinstance(row_csv["seasons"], list):
                        row_csv["seasons"] = ",".join(row_csv["seasons"])
                    if isinstance(row_csv["occasions"], list):
                        row_csv["occasions"] = ",".join(row_csv["occasions"])
                    writer.writerow(row_csv)
            print(f"Exported {len(dataset)} items to {output_csv}")

    finally:
        db.close()

if __name__ == "__main__":
    export_dataset()
