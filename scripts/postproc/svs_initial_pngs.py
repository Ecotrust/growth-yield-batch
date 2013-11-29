# Run in windows with WinSVS installed
import os
import glob

def svs_to_png(svs):
    if os.path.exists("%s.png" % svs):
        print "skipping", svs
        return
    # tweak manually then get display > command line options
    cmd = "c:\\fvsbin\\winsvs.exe -A216 -E400 -S16 -D314 -L58 -C%s.bmp %s" % (svs, svs)
    print cmd
    os.system(cmd)
    cmd = '"c:\\Program Files (x86)\\ImageMagick\\convert.exe" %s.bmp %s.png' % (svs, svs)
    print cmd
    os.system(cmd)
    os.remove("%s.bmp" % svs)


if __name__ == '__main__':
    for svs in glob.glob("*_001.svs"):
        svs_to_png(svs)




