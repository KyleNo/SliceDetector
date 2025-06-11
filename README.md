# Path-Faithful Dynamic Slices

## Usage

```commandline
python main <input_file> [-o <output_file>]
```

example
```commandline
python main input/example1.txt -o output/output1.txt
```

## Input format
Input files should be 3 sections each separated by a double newline.

The first section is a program schema. There can only be one assignment
per line. The predicate must directly follow an `if` keyword.
`else` and `fi` should be on their own lines.

The second section is two lines. The first line is a string of T's and F's,
representing the evaluation of the predicates encountered on the path.
The second line is the number of assignments after the last conditional
encountered on the execution path. If there are no conditionals on
the execution path, omit the first line

The third section is the variable names that should be preserved.
Each should be separated by commas.