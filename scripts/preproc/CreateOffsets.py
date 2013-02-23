import glob
import sys
import os
import shutil


def log(x):
    print x


def create_offsets(baserxdir, outdir, num_offsets=10, period=5):
    orig_keys = glob.glob(os.path.join(baserxdir, '*_original.key'))
    if len(orig_keys) < 1:
        raise Exception("Need at least one *_original.key file")
    for inkey in orig_keys:
        keyprefix = os.path.splitext(os.path.basename(inkey))[0]
        keybase = keyprefix.replace('_original','')
        # GO = grow only = a special case
        # if keybase == "GO":
        #     continue
        log("Processing %s keys" % keybase)

        # Create XX_01.key
        outkey = os.path.join(outdir, keybase + "_01.key")
        shutil.copy(inkey, outkey)
        log("\tbase key %s_01.key" % keybase)

        for offset in range(2, num_offsets):
            log("\toffset key %s" % offset)
            offset_years = (offset - 1) * period
            # Create the XX_YY.key offsets
            outkey = os.path.join(outdir, "%s_%02d.key" % (keybase, offset))
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
