import json
import os

def deduplicate_listings(listings):
    seen = set()
    deduped = []
    for l in listings:
        url = l.get("funda_url") or l.get("object_detail_page_relative_url")
        if url and url not in seen:
            deduped.append(l)
            seen.add(url)
    return deduped

def main():
    db_path = os.path.join(os.path.dirname(__file__), "../database.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    changed = False
    for pid, profile in db.items():
        orig_count = len(profile.get("listings", []))
        deduped = deduplicate_listings(profile.get("listings", []))
        if len(deduped) != orig_count:
            print(f"Profile {pid}: {orig_count} -> {len(deduped)} (deduplicated)")
            db[pid]["listings"] = deduped
            changed = True
    if changed:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print("database.json deduplicated and saved.")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()
