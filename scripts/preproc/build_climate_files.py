import os

#### DEPRECATED .. see build_cond_dir.py

master_climate = "C:/Users/mperry/Desktop/FVSClimAttrs_NoClimateAdded.csv"
outdir = "E:/workspace/testout"

if __name__ == "__main__":
    header = None
    current_id = None
    lines = []
    with open(master_climate, 'r') as fh:
        for line in fh:
            if not header:
                header = line
                continue

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
                # clear 
                lines = []

            lines.append(line)
            print condid
