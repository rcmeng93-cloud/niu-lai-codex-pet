#!/usr/bin/env python3
"""Install this Codex v2 pet into a local Codex home."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-home",
        help="override the destination Codex home; defaults to CODEX_HOME or ~/.codex",
    )
    parser.add_argument("--dry-run", action="store_true", help="show the destination without copying")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pet_id = manifest.get("id")
    if not isinstance(pet_id, str) or not pet_id:
        raise SystemExit("pet.json id must be a non-empty string")
    if manifest.get("spriteVersionNumber") != 2:
        raise SystemExit("pet.json must declare spriteVersionNumber 2")

    source_sprite = project_root / manifest.get("spritesheetPath", "")
    if not source_sprite.is_file():
        raise SystemExit(f"spritesheet not found: {source_sprite}")

    codex_home = Path(
        args.codex_home
        or os.environ.get("CODEX_HOME")
        or (Path.home() / ".codex")
    ).expanduser()
    destination = codex_home / "pets" / pet_id

    if args.dry_run:
        print(destination)
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    installed_manifest = dict(manifest)
    installed_manifest["spritesheetPath"] = "spritesheet.webp"
    (destination / "pet.json").write_text(
        json.dumps(installed_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(source_sprite, destination / "spritesheet.webp")

    print(f"Installed {pet_id} to {destination}")
    print("Restart Codex or refresh the pet list to load it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
