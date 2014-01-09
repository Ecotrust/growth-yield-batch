import sys
import os

master_climate = sys.argv[1]
outdir = sys.argv[2]

if os.path.exists(outdir):
    raise Exception(outdir + " already exists!")

os.mkdir(outdir)

if __name__ == "__main__":
    header = None
    current_id = None
    lines = []
    with open(master_climate, 'r') as fh:
        for line in fh:

            # Get the header and stash it away
            if not header:
                header = line
                continue

            # start collecting the lines
            lines.append(line)

            # Grab condition id
            condid = line.split(",")[0]
            if not current_id:
                current_id = condid

            if condid != current_id:
                # hit a new cond_id
                # save the old one
                with open(os.path.join(outdir, current_id + ".cli"), 'w') as out:
                    out.write(header)
                    out.writelines(lines)
                current_id = condid
                # and clear 
                lines = []

    # save the final one
    with open(os.path.join(outdir, current_id + ".cli"), 'w') as out:
        out.write(header)
        out.writelines(lines)
        current_id = condid
