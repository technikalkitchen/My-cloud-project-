import sys
import os
import shutil
import re

ARCHIVE = "docs/B_items/Cross_Item_Notes_ARCHIVE.md"
PROTOCOL = "docs/TEAM_PROTOCOL.md" 
REGISTRY = "docs/B_items/Item_Registry.md"

R_MAPPING = {
    "TEAM_PROTOCOL": {
        "rules": ["R-09", "R-12", "R-16", "R-23", "R-24", "R-25"],
        "anchor": "## بخش ۳ — قوانین ارتباطی (تغییرناپذیر)"
    },
    "Item_09": {"rules": ["R-01", "R-15"], "anchor": "## Item_09"},
    "Item_11": {"rules": ["R-02", "R-03"], "anchor": "## Item_11"},
    "Item_12": {"rules": ["R-04", "R-05", "R-06", "R-07"], "anchor": "## Item_12"},
    "Item_01": {"rules": ["R-11"], "anchor": "## Item_01"},
    "Item_03": {"rules": ["R-29"], "anchor": "## Item_03"},
    "Item_06": {"rules": ["R-30"], "anchor": "## Item_06"},
    "Item_15": {"rules": ["R-31a", "R-31b"], "anchor": "## Item_15"},
    "Item_04": {"rules": ["R-32"], "anchor": "## Item_04"}
}

CIN_MAPPING = {
    "Item_01": ["CIN-1"],
    "Item_03": ["CIN-8", "CIN-9"],
    "Item_04": ["CIN-10"],
    "Item_06": ["CIN-2", "CIN-3", "CIN-6"],
    "Item_11": ["CIN-4"],
    "Item_12": ["CIN-5"],
    "Item_14": ["CIN-11"],
    "Item_15": ["CIN-12"],
    "Item_16": ["CIN-13"],
    "Package D": ["CIN-7", "CIN-14"]
}

def extract_block(text, block_id):
    pattern = re.compile(rf'###\s*{re.escape(block_id)}.*?(?=\n###|\Z)', re.DOTALL)
    match = pattern.search(text)
    return match.group(0).strip() + "\n\n" if match else None

def insert_after_anchor(content, anchor_prefix, text_to_insert):
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith(anchor_prefix):
            return "".join(lines[:i+1]) + "\n" + text_to_insert + "".join(lines[i+1:])
    return None

def main():
    for f in [ARCHIVE, PROTOCOL, REGISTRY]:
        if not os.path.isfile(f):
            print(f"[ABORT] File missing: {f}")
            sys.exit(1)

    with open(ARCHIVE, "r", encoding="utf-8", newline='') as f:
        archive_text = f.read()
    with open(PROTOCOL, "r", encoding="utf-8", newline='') as f:
        protocol_text = f.read()
    with open(REGISTRY, "r", encoding="utf-8", newline='') as f:
        registry_text = f.read()

    new_protocol = protocol_text
    new_registry = registry_text
    changes_made = 0

    for target, info in R_MAPPING.items():
        target_text = new_protocol if target == "TEAM_PROTOCOL" else new_registry
        anchor = info["anchor"]
        for rule in info["rules"]:
            if f"### {rule}" in target_text:
                continue
            block = extract_block(archive_text, rule)
            if block:
                updated_text = insert_after_anchor(target_text, anchor, block)
                if updated_text:
                    target_text = updated_text
                    changes_made += 1
                else:
                    print(f"[WARNING] Anchor '{anchor}' not found in {target}. Skipping {rule}.")
        if target == "TEAM_PROTOCOL":
            new_protocol = target_text
        else:
            new_registry = target_text

    for target, cin_list in CIN_MAPPING.items():
        anchor = f"## {target}"
        for cin_id in cin_list:
            if cin_id in new_registry:
                continue
            block = extract_block(archive_text, cin_id)
            if block:
                updated_text = insert_after_anchor(new_registry, anchor, block)
                if updated_text:
                    new_registry = updated_text
                    changes_made += 1
                else:
                    print(f"[WARNING] Anchor '{anchor}' not found for {cin_id}.")

    if changes_made == 0:
        print("[SKIP] No new rules or CINs to add. Files are up to date.")
        sys.exit(0)

    shutil.copy2(PROTOCOL, PROTOCOL + ".bak")
    shutil.copy2(REGISTRY, REGISTRY + ".bak")
    print("[BACKUP] Created .bak files.")

    with open(PROTOCOL, "w", encoding="utf-8", newline='') as f:
        f.write(new_protocol)
    with open(REGISTRY, "w", encoding="utf-8", newline='') as f:
        f.write(new_registry)

    print(f"[OK] Migration complete. Applied {changes_made} changes.")
    print("[DONE] Archive file left untouched as requested.")

if __name__ == "__main__":
    main()
