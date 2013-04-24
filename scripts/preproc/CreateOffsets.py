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

    go_keys = glob.glob(os.path.join(baserxdir, '*_growonly.key'))
    if len(go_keys) != 1:
        log("!!!!! Need one and only one *_growonly.key file per directory")
        sys.exit(1)

    inkey = orig_keys[0]
    gokey = go_keys[0]
    keybase = os.path.splitext(os.path.basename(inkey))[0].replace("_original", "")
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

    # copy the grow-only, assume
    outkey = os.path.join(outdir, keybase + "_99.key")
    shutil.copy(gokey, outkey)
    log("\tgrow only key %s_99.key" % keybase)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        create_offsets(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 5:
        create_offsets(sys.argv[1], sys.argv[2], num_offsets=int(sys.argv[3]), period=int(sys.argv[4]))
    else:
        raise Exception
