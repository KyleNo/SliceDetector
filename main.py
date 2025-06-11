from collections import defaultdict

from schema import *
from slices import find_slice
from parser import parse_input
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SliceDetector",
        description="Finds Non-Trivial Path Faithful Dynamic Slices of Linear Program Schema"
    )
    parser.add_argument('input')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()
    with open(args.input) as f:
        text = f.read()
        schema, exec_path, v = parse_input(text)
    result = find_slice(schema, exec_path, v)
    if result is None:
        print("No non-trivial path found :(")
        exit()
    lines = [line for i, line in enumerate(text.split("\n\n")[0].split("\n")) if i not in result]
    if args.output is None:
        for line in lines:
            print(line)
    else:
        with open(args.output, "w") as wf:
            for line in lines:
                wf.write(line + "\n")


