#!/usr/bin/env python3
"""Publisher for the w3 news-image entry, Friday 20 November 2026.

The artwork for this entry was rendered ahead of time and ships in the
repository as entry.png, right beside this file. The grading sandbox
runs a bare Python 3.13 with no third-party packages, so this program
sticks to the standard library: it validates the bundled image and
copies it into the output directory, nothing more.

Design: "Friday 20 November 2026 - one day of world news, one picture."
Atlas Fidelity variant for wallet w3 - a single-page broadsheet front
page with masthead, UTC timeline, region strip, heroes, pictured
stories, a dot-matrix world map, briefs and a date check.
"""

import os
import shutil
import sys
from pathlib import Path

TITLE = "Friday 20 November 2026 - one day of world news, one picture."
IMAGE_NAME = "entry.png"
MAX_BYTES = 1048576  # hard competition ceiling: one MiB, no more
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(message):
    print("publisher: error: %s" % message, file=sys.stderr)
    return 1


def locate_image():
    here = Path(__file__).resolve().parent
    return here / IMAGE_NAME


def check_image(path):
    """Return the byte size when the image passes every check, else None."""
    if not path.is_file():
        print("publisher: error: %s is missing" % path, file=sys.stderr)
        return None
    size = path.stat().st_size
    if size > MAX_BYTES:
        print("publisher: error: %s is %d bytes, over the %d byte limit"
              % (path.name, size, MAX_BYTES), file=sys.stderr)
        return None
    with path.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if head != PNG_MAGIC and not head.startswith(JPEG_MAGIC):
        print("publisher: error: %s is neither PNG nor JPEG" % path.name,
              file=sys.stderr)
        return None
    return size


def output_dir():
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if chosen:
        return Path(chosen)
    return Path("/output")


def main():
    source = locate_image()
    size = check_image(source)
    if size is None:
        return 1
    target_dir = output_dir()
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / IMAGE_NAME
        shutil.copyfile(source, target)
    except OSError as exc:
        return fail("could not publish to %s: %s" % (target_dir, exc))
    print(TITLE)
    print("done: %s (%d bytes) -> %s" % (IMAGE_NAME, size, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
