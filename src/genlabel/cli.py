#!/usr/bin/env python3
# ruff: noqa: F403

from __future__ import annotations

import logging
from argparse import ArgumentParser
from itertools import islice

import build123d as bd

# from build123d import *
from build123d import (
    BuildPart,
    Location,
    add,
    export_step,
)
from ocp_vscode import Camera, set_defaults, show

logger = logging.getLogger(__name__)

# logging.basicConfig(level=logging.DEBUG)
set_defaults(reset_camera=Camera.CENTER)

common_args = ArgumentParser(add_help=False)


# Taken from Python 3.12 documentation.
def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def run(argv: list[str] | None = None):
    parser = ArgumentParser(description="Generate pred-style gridfinity bin labels")
    parser.add_argument(
        "-w",
        "--width",
        help="Label width, in gridfinity units. Default: %(default)s",
        metavar="WIDTH_U",
        default="1",
    )
    parser.add_argument("labels", nargs="*", metavar="LABEL")
    parser.add_argument(
        "-d",
        "--divisions",
        help="How many areas to divide a single label into. If more labels that this are requested, multiple labels will be generated.",
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output filename. [Default: %(default)s]",
        default="label.step",
    )
    args = parser.parse_args(argv)

    args.width = int(args.width.rstrip("u"))
    args.divisions = args.divisions or len(args.labels)

    y = 0
    with BuildPart() as part:
        for labels in batched(args.labels, args.divisions):
            # pred.body(args.width)
            label = generate_single_label(args.width, args.divisions, labels)
            label.location = Location((0, y))
            add(label)
            y -= 13

    if args.output.endswith(".stl"):
        bd.export_stl(part.part, args.output)
    elif args.output.endswith(".step"):
        export_step(part.part, args.output)
    else:
        print(f"Error: Do not understand output format '{args.output}'")

    show(part)


# _FRAGMENTS = {
#     "hexhead": _fragment_hexhead,
#     "bolt": _fragment_bolt,
#     "washer": _fragment_washer,
#     "hexnut": _fragment_hexnut,
#     "nut": _fragment_hexnut,
#     "variable_resistor": _fragment_variable_resistor,
# }

if __name__ == "__main__":
    divisions = 0
    filename = "label.step"

    labels = [
        "{hexnut} M6 {hexnut}",
        "{washer} M3",
        "{hexhead} {bolt(12)}\nM3×12",
        "{variable_resistor}",
        "{hexhead} {bolt(30)}\nM4×30",
    ]
    # divisions = divisions or len(labels)

    run([str(x) for x in [1, *labels, "--divisions", "1"]])
