import fnmatch
import os
from shutil import copyfile

LOOKUP = {}
for line in open("stand_age_lookup.csv", 'r').readlines()[1:]:
    items = line.strip().split(",")
    LOOKUP[items[0]] = items[2]

OUTDIR = "C:\\Users\\mperry\\Desktop\\Dave Walters Deliverables\\20130529\\prepped_stand_age_adjusted"


def lookup_age(age_code):
    code = age_code.strip()
    age = int(LOOKUP[code])
    return "%3d" % age


def matches():
    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, '*.std'):
            yield os.path.join(root, filename)


def main():
    for std in matches():
        stdinfo = open(std, 'r').readlines()[0]
        age_code = stdinfo[37:40]
        try:
            age = lookup_age(age_code)

            # new_stdinfo = stdinfo[:37] + age + stdinfo[40:]

            # # write new standinfo line to new file
            # parts = std.split("\\")[1:]
            # out_std = os.path.join(OUTDIR, *parts)
            # with open(out_std,'w') as fh:
            #     fh.write(new_stdinfo)
            # # print "open(%s,'w').write(%s)" % (out_std, new_stdinfo)

            # # copy fvs file
            # in_fvs = std.replace(".std",".fvs")
            # out_fvs = out_std.replace(".std",".fvs")
            # copyfile(in_fvs, out_fvs)
            # # print "copyfile(%s, %s)" % (in_fvs, out_fvs)
            pass

        except KeyError:
            print std



if __name__ == '__main__':
    main()
