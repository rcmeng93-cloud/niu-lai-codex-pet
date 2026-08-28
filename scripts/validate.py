#!/usr/bin/env python3
"""Validate the portable Niu Lai Codex pet project without third-party packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_SIZE = (1536, 2288)


def webp_dimensions(path: Path) -> tuple[int, int, bool]:
    """Read dimensions and alpha usage from the first supported WebP chunk."""
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a RIFF WebP file")

    offset = 12
    while offset + 8 <= len(data):
        fourcc = data[offset : offset + 4]
        size = int.from_bytes(data[offset + 4 : offset + 8], "little")
        payload = data[offset + 8 : offset + 8 + size]
        if len(payload) != size:
            raise ValueError("truncated WebP chunk")

        if fourcc == b"VP8X" and len(payload) >= 10:
            width = 1 + int.from_bytes(payload[4:7], "little")
            height = 1 + int.from_bytes(payload[7:10], "little")
            return width, height, bool(payload[0] & 0x10)

        if fourcc == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
            width = 1 + ((payload[1] | (payload[2] << 8)) & 0x3FFF)
            height = 1 + (
                (payload[2] >> 6)
                | (payload[3] << 2)
                | ((payload[4] & 0x0F) << 10)
            )
            return width, height, bool(payload[4] & 0x10)

        if fourcc == b"VP8" and len(payload) >= 10:
            if payload[3:6] != b"\x9D\x01\x2A":
                raise ValueError("unsupported lossy VP8 frame")
            width = int.from_bytes(payload[6:8], "little") & 0x3FFF
            height = int.from_bytes(payload[8:10], "little") & 0x3FFF
            return width, height, False

        offset += 8 + size + (size & 1)

    raise ValueError("no supported VP8, VP8L, or VP8X image chunk found")


def validate(project_root: Path) -> dict[str, object]:
    errors: list[str] = []
    manifest_path = project_root / "pet.json"
    if not manifest_path.is_file():
        return {"ok": False, "errors": [f"missing {manifest_path}"], "warnings": []}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "errors": [f"invalid pet.json: {exc}"], "warnings": []}

    required = ("id", "displayName", "description", "spriteVersionNumber", "spritesheetPath")
    for key in required:
        if key not in manifest:
            errors.append(f"pet.json is missing {key}")

    if manifest.get("spriteVersionNumber") != 2:
        errors.append("spriteVersionNumber must be 2")

    sprite_value = manifest.get("spritesheetPath")
    if not isinstance(sprite_value, str) or not sprite_value:
        errors.append("spritesheetPath must be a non-empty string")
        sprite_path = project_root / "assets" / "spritesheet.webp"
    else:
        sprite_path = Path(sprite_value)
        if not sprite_path.is_absolute():
            sprite_path = project_root / sprite_path

    if not sprite_path.is_file():
        errors.append(f"missing spritesheet: {sprite_path}")
        dimensions = None
        has_alpha = False
    else:
        try:
            dimensions = webp_dimensions(sprite_path)
            has_alpha = dimensions[2]
            if dimensions[:2] != EXPECTED_SIZE:
                errors.append(
                    f"spritesheet must be {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, got {dimensions[0]}x{dimensions[1]}"
                )
            if not has_alpha:
                errors.append("spritesheet does not advertise an alpha channel")
        except (OSError, ValueError) as exc:
            dimensions = None
            has_alpha = False
            errors.append(f"invalid spritesheet: {exc}")

    return {
        "ok": not errors,
        "project": str(project_root),
        "manifest": str(manifest_path),
        "spritesheet": str(sprite_path),
        "spriteVersionNumber": manifest.get("spriteVersionNumber"),
        "dimensions": dimensions[:2] if dimensions else None,
        "alpha": has_alpha,
        "errors": errors,
        "warnings": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="project directory containing pet.json and assets/",
    )
    args = parser.parse_args()
    result = validate(Path(args.project_root).expanduser().resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
