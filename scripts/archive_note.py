#!/usr/bin/env python3
"""Copy a drafted illustrated note and its real assets into an Obsidian vault.

Standard library only. Checks files, basic frontmatter fields, figure markers,
and output paths; it does not check factual or visual correctness.
"""

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import sys


FIGURE = re.compile(r"<!--\s*figure:([A-Za-z0-9_-]+)\s*-->")


def safe_name(value):
    value = re.sub(r'[\x00-\x1f<>:"/\\|?*#\[\]^]', "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .-")
    if not value:
        raise ValueError("A filename cannot be empty")
    return value


def in_vault(vault, relative):
    part = Path(relative)
    if part.is_absolute():
        raise ValueError("--area and --image-root must be relative to the vault")
    result = (vault / part).resolve()
    if not result.is_relative_to(vault):
        raise ValueError(f"Output path leaves the vault: {relative}")
    return result


def existing_file(value, parent):
    path = Path(value).expanduser()
    path = (parent / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_file():
        raise ValueError(f"Input file does not exist: {path}")
    return path


def image_extension(path):
    with path.open("rb") as handle:
        header = handle.read(16)
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"
    raise ValueError(f"Expected a PNG, JPEG, or WebP image: {path}")


def available_note(directory, stem):
    candidate = directory / f"{stem}.md"
    number = 2
    while candidate.exists():
        candidate = directory / f"{stem}-v{number}.md"
        number += 1
    return candidate


def prepare(args):
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        raise ValueError(f"Vault does not exist: {vault}")
    note = existing_file(args.note, Path.cwd())
    content = note.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
    if not frontmatter:
        raise ValueError("The note needs YAML frontmatter")
    for field in ("title", "type", "tags", "created", "status"):
        if not re.search(rf"^{field}:\s*\S", frontmatter[1], re.M):
            raise ValueError(f"Missing basic frontmatter field: {field}")

    images = []
    manifest_parent = note.parent
    if args.images:
        manifest = existing_file(args.images, Path.cwd())
        manifest_parent = manifest.parent
        images = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(images, list):
            raise ValueError("Image manifest must be a JSON array")
    if not images and not args.text_only:
        raise ValueError("No images supplied; use --text-only for a text-only result")
    if images and args.text_only:
        raise ValueError("--text-only cannot be combined with nonempty images")

    markers = Counter(FIGURE.findall(content))
    ids = []
    prepared = []
    for item in images:
        if not isinstance(item, dict):
            raise ValueError("Each image manifest entry must be an object")
        image_id = str(item.get("id", ""))
        if not re.fullmatch(r"[A-Za-z0-9_-]+", image_id):
            raise ValueError(f"Invalid image id: {image_id}")
        ids.append(image_id)
        image = existing_file(item["path"], manifest_parent)
        prompt = existing_file(item["prompt"], manifest_parent)
        caption = str(item.get("caption") or item.get("alt") or "").strip()
        if not caption:
            raise ValueError(f"Missing image caption: {image_id}")
        filename = f"{image_id}-{safe_name(image.stem)}{image_extension(image)}"
        prepared.append({"id": image_id, "source": image, "prompt": prompt,
                         "filename": filename, "caption": caption})
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate image ids in manifest")
    if markers != Counter({image_id: 1 for image_id in ids}):
        raise ValueError("Figure markers and manifest ids must match exactly once")

    records = [existing_file(value, Path.cwd()) for value in args.record]
    record_names = [safe_name(path.name) for path in records]
    if len(record_names) != len(set(record_names)):
        raise ValueError("Record filenames must be unique")
    directory = in_vault(vault, args.area)
    stem = safe_name(args.name or note.stem)
    destination = available_note(directory, stem)
    image_root = in_vault(vault, args.image_root)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    assets = image_root / f"{stem}-{stamp}"
    number = 2
    while assets.exists():
        assets = image_root / f"{stem}-{stamp}-{number}"
        number += 1

    replacements = {}
    for item in prepared:
        target = assets / item["filename"]
        relative = target.relative_to(vault).as_posix()
        replacements[item["id"]] = f"![[{relative}]]\n\n{item['caption']}"
    content = FIGURE.sub(lambda match: replacements[match[1]], content)
    plan = {"note_path": str(destination), "images_count": len(prepared),
            "image_dir": str(assets) if prepared or records else None,
            "image_paths": [str(assets / item["filename"]) for item in prepared],
            "record_paths": [str(assets / "records" / name) for name in record_names],
            "dry_run": args.dry_run}
    return content, prepared, records, record_names, destination, assets, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", required=True)
    parser.add_argument("--images", help="JSON image manifest")
    parser.add_argument("--vault", required=True, help="Absolute path to an existing Obsidian vault")
    parser.add_argument("--area", required=True, help="Note folder relative to vault")
    parser.add_argument("--image-root", default="Attachments/illustrated-knowledge",
                        help="Image folder relative to vault")
    parser.add_argument("--name", help="Final filename stem; defaults to draft stem")
    parser.add_argument("--record", action="append", default=[])
    parser.add_argument("--text-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        content, images, records, names, destination, assets, plan = prepare(args)
        if not args.dry_run:
            made_assets = False
            made_note = False
            try:
                if images or records:
                    assets.mkdir(parents=True, exist_ok=False)
                    made_assets = True
                if images:
                    (assets / "prompts").mkdir()
                    for item in images:
                        shutil.copy2(item["source"], assets / item["filename"])
                        shutil.copy2(item["prompt"], assets / "prompts" / f"{item['id']}.md")
                if records:
                    (assets / "records").mkdir()
                    for record, name in zip(records, names):
                        shutil.copy2(record, assets / "records" / name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("x", encoding="utf-8") as handle:
                    made_note = True
                    handle.write(content)
            except Exception:
                if made_note:
                    destination.unlink()
                if made_assets:
                    shutil.rmtree(assets)
                raise
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
