# Run in windows with WinSVS installed
import os
import glob

FVSOUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "__svs_test", "tmpout"))
GIFOUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "__svs_test", "gifs"))

def index_to_bmps(index):
    lines = open(index,'r').readlines()
    svs_list = []
    for line in lines[1:]:
        parts = line.split('" "')
        svs = parts[1].replace('"', '').strip()
        name = parts[0]
        if "Post cutting" in name:
            # pop the last one which was pre-cut
            svs_list.pop()
        svs_list.append(svs)

    for svs in svs_list:
        svs_to_bmp(svs)


def svs_to_bmp(svs):
    cmd = "e:\\git\\growth-yield-batch\\fvsbin\\winsvs.exe -A292 -E320 -S27 -D252 -L46 -C%s.bmp %s" % (svs, svs)
    print cmd
    os.system(cmd)


if __name__ == '__main__':
    os.chdir(FVSOUT)
    cmds = []
    for rundir in glob.glob("var*"):
        os.chdir(rundir)

        indexes = [
            "varPN_rx1_cond29106_site2_00_index.svs",
            "varPN_rx21_cond29106_site2_00_index.svs",
            "varPN_rx24_cond29106_site2_00_index.svs",
            "varPN_rx6_cond29106_site2_00_index.svs",
        ]

        for index in glob.glob("*_index.svs"):
            if index not in indexes:
                continue

            # uncomment to recreate bmps
            index_to_bmps(index)

            prefix = index.replace("_index.svs","")
            bmp_glob = os.path.join(rundir, prefix + "*.svs.bmp")
            gif = os.path.join(GIFOUT, prefix + ".gif")
            cmd = '"c:\\Program Files (x86)\\ImageMagick\\convert.exe" -delay 60 -resize 75%% %s %s' % (bmp_glob, gif)
            cmds.append(cmd)

        os.chdir("..")

    print
    print "=" * 80
    for cmd in cmds:
        print cmd
        os.system(cmd)


