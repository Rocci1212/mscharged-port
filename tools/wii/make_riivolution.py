#!/usr/bin/env python3
"""Build a Riivolution package from the tweak series.

Inputs (all produced by earlier CI steps):
  build/wii/vanilla/main.dol          -- untouched decomp build
  build/wii/patched/main.dol          -- decomp build with the tweak series
  build/wii/patched/                  -- any other changed files (data, modules)

Output:
  build/artifacts/<name>-riivolution.zip
    /riivolution/patch.xml
    /riivolution/<files referenced by the XML>
"""

import argparse
import hashlib
import zipfile
from pathlib import Path

# The four disc variants the project already targets.
GAME_IDS = {
    "R4QE01": "USA rev 1",
    "R4QP01": "Europe rev 1 or 2",
}

def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()

def write_patch_xml(out_dir: Path, files: list[Path], title: str):
    # <wiidisc version="1" root="/riivolution"> is the standard root element.
    # <id> restricts the patch to the disc(s) it was built against.
    # <options> creates toggleable feature entries in the Riivolution menu.
    # <patch> does the actual replacement.
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<wiidisc version="1" root="/riivolution">',
           '  <id game="R4QE01" />',
           '  <id game="R4QP01" />',
           f'  <options>',
           f'    <section name="{title}">',
           f'      <option name="Enable tweaks" default="1" />',
           f'    </section>',
           f'  </options>',
           '  <patch id="tweaks">']
    for f in files:
        rel = f.relative_to(out_dir)
        xml.append(f'    <file disc="{rel.as_posix()}" external="{rel.as_posix()}" />')
    xml.append('  </patch>')
    xml.append('</wiidisc>')
    (out_dir / "patch.xml").write_text("\n".join(xml) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vanilla", required=True, type=Path)
    ap.add_argument("--patched", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--name", default="recharged-strikers-tweaks")
    args = ap.parse_args()

    stage = args.output_dir / "riivolution"
    stage.mkdir(parents=True, exist_ok=True)

    changed = []
    for p in args.patched.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(args.patched)
        v = args.vanilla / rel
        if not v.exists() or sha1(v) != sha1(p):
            dest = stage / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
            changed.append(dest)

    if not changed:
        raise SystemExit("no changes between vanilla and patched builds")

    # main.dol is the usual carrier; flag if it's missing so CI catches a
    # decomp that stopped producing it.
    if not (stage / "main.dol").exists():
        print("warning: main.dol not among changed files; code tweaks may be missing")

    write_patch_xml(stage, changed, "Recharged tweaks")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive = args.output_dir / f"{args.name}-riivolution.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(stage / "patch.xml", "riivolution/patch.xml")
        for f in changed:
            z.write(f, f"riivolution/{f.relative_to(stage).as_posix()}")

    print(f"wrote {archive} ({len(changed)} changed files)")

if __name__ == "__main__":
    main()