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


"""
montage ../*.bmp -geometry 120x120>+1+1 -tile 21x9 montage_geom.jpg

montage *rx1*.bmp -geometry +1+1 -tile 11x1 svs_rx1_NoClimate.jpg
montage *rx4*.bmp -geometry +1+1 -tile 13x1 svs_rx4_NoClimate.jpg
montage *rx5*.bmp -geometry +1+1 -tile 12x1 svs_rx5_NoClimate.jpg
montage *rx6*.bmp -geometry +1+1 -tile 13x1 svs_rx6_NoClimate.jpg
montage *rx7*.bmp -geometry +1+1 -tile 12x1 svs_rx7_NoClimate.jpg
montage *rx8*.bmp -geometry +1+1 -tile 13x1 svs_rx8_NoClimate.jpg
montage *rx9*.bmp -geometry +1+1 -tile 13x1 svs_rx9_NoClimate.jpg
montage svs_rx*_NoClimate.jpg -geometry +1+1 -tile 1x7 svs_allrx_NoClimate.jpg
"""

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


