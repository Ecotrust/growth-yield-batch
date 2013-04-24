import glob
import sys
import os
import shutil


def log(x):
    print x


def create_offsets(baserxdir, outdir, num_offsets=4, period=5):
    orig_keys = glob.glob(os.path.join(baserxdir, '*_original.key'))
    if len(orig_keys) != 1:
        log("!!!!! Need one and only one *_original.key file per directory")
        sys.exit(1)

    for inkey in orig_keys:
        keybase = os.path.splitext(os.path.basename(inkey))[0].replace("_original", "")
        # GO = grow only = a special case
        # if keybase == "GO":
        #     continue
        log("Processing %s keys" % keybase)

        outkey = os.path.join(outdir, keybase + "_00.key")
        shutil.copy(inkey, outkey)
        log("\tbase key %s_00.key" % keybase)

        for offset in range(1, num_offsets + 1):
            offset_years = (offset) * period
            outkey = os.path.join(outdir, "%s_%02d.key" % (keybase, offset))
            log("\toffset key %s_%02d.key" % (keybase, offset))
            ofh = open(outkey, 'w')
            for line in open(inkey, 'r'):
                newline = line
                if line.startswith("Offset ="):
                    newline = "Offset = %d\r\n" % offset_years
                ofh.write(newline)
            ofh.close()

        # Create final key; grow only
        # gokey = os.path.join(baserxdir, "GO_01.key")
        # outkey = os.path.join(outdir, "%s_%02d.key" % (keybase, num_offsets))
        # shutil.copy(gokey, outkey)
        # log("  grow-only key GO_%s.key" % num_offsets)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        create_offsets(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 5:
        create_offsets(sys.argv[1], sys.argv[2], num_offsets=int(sys.argv[3]), period=int(sys.argv[4]))
    else:
        raise Exception
