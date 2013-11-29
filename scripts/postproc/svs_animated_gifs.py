# Run in windows with WinSVS installed
import os
import glob

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
    # tweak manually then get display > command line options
    cmd = "c:\\fvsbin\\winsvs.exe -A216 -E400 -S16 -D314 -L58 -C%s.bmp %s" % (svs, svs)
    print cmd
    os.system(cmd)
    # cmd = '"c:\\Program Files (x86)\\ImageMagick\\convert.exe" %s.bmp %s.png' % (svs, svs)
    # print cmd
    # os.system(cmd)


if __name__ == '__main__':
    cmds = []

    for index in glob.glob("*_index.svs"):
        # if index not in indexes:
        #     continue

        # uncomment to recreate bmps
        index_to_bmps(index)

        prefix = os.path.basename(index).replace("_index.svs","")
        bmp_glob = os.path.join('.', prefix + "*.svs.bmp")
        gif = os.path.join('.', prefix + ".gif")
        cmd = '"c:\\Program Files (x86)\\ImageMagick\\convert.exe" -delay 60 -resize 75%% %s %s' % (bmp_glob, gif)
        cmds.append(cmd)

    print
    print "=" * 80
    for cmd in cmds:
        print cmd
        os.system(cmd)


