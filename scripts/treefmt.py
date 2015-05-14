#!/usr/bin/env python
from __future__ import print_function
import math
from collections import OrderedDict

fields = """Plot ID
Tree Number
Tree Count
Tree History
Species
Diameter at Breast Height
DBH Increment
Live Height
Height to Top Kill
Height Increment
Crown Ratio Code
Damage Code 1
Severity Code 1
Damage Code 2
Severity Code 2
Damage Code 3
Severity Code 3
Tree Value Class Code
Cut/Leave Prescription Code
Plot slope percent
Plot aspect in degrees
Plot habitat type code
Plot topographic position code
Plot site preparation code
Tree Age""".split('\n')

# As defined in projects/ForestPlanner/rx/include/input_formats.txt
treefmt = "I6,I3,F6.0,I1,A3,F5.1,F3.1,F3.0,F3.0,F4.1,I1,6I2,I1,I1,I2,I3,I3,I1,I1,F4.0"

treefmt = treefmt.split(",")

valid_types = "IFA"


def linepos(treefmt):
    line = 0
    for fmt in treefmt:
        mult = 1
        ftype, num = fmt[0], fmt[1:]
        if ftype not in valid_types:
            # assume it's a number
            mult = int(ftype)
            ftype, num = num[0], num[1:]
        num = int(math.floor(float(num)))
        for x in range(mult):
            start = line
            line += num
            yield (start, line)


def parse_line(line, columns):
    for field, cr in columns.items():
        val = line.rstrip()[cr[0]:cr[1]]
        yield (field, val)


if __name__ == '__main__':
    colstops = list(linepos(treefmt))
    print()
    assert len(fields) == len(colstops)
    columns = OrderedDict(zip(fields, colstops))
    print(columns)

    import glob
    for fvs in glob.glob('*.fvs'):
        print(fvs)
        with open(fvs, 'r') as fh:
            for line in fh.readlines():
                sub = {'Tree Count': columns['Tree Count']}
                for field, val in parse_line(line, sub):
                    print("{:>30}: '{}'".format(field, val))
    print


