import sys, os, time

wavfile = sys.argv[1]
labfile = sys.argv[2]
outfile = sys.argv[3]

with open(labfile) as fh:
    lablines = fh.readlines()


pads = []
silencelen = 1
i = 0
for labline in lablines:
    (start, end, text) = labline.split(" ")
    point = float(end)+silencelen*i
    print(point)
    pads.append("pad 1@%.2f" % point)
    i += 1

cmd = "sox %s %s %s" % (wavfile, outfile, " ".join(pads))
print(cmd)
os.system(cmd)

