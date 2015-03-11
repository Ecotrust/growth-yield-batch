from __future__ import print_function
import math

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
            line += num
            yield line

if __name__ == '__main__':
    print(list(linepos(treefmt)))