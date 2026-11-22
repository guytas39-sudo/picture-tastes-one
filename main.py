#!/usr/bin/env python3
"""Write the pre-drawn picture to the output directory.

Stdlib only: the grader runs in a stock Python 3.13 image with
nothing installed. The picture itself is drawn at build time by
draw_image.py and shipped as entry.png next to this file.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(
        os.path.join(HERE, "entry.png"),
        os.path.join(out_dir, "entry.png"),
    )


if __name__ == "__main__":
    main()
