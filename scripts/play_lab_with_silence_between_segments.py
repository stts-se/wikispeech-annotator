import sys, os, time


wavfile = sys.argv[1]
labfile = sys.argv[2]

with open(labfile) as fh:
    lablines = fh.readlines()

for labline in lablines:
    (start, end, text) = labline.split(" ")
    cmd = "play -q %s trim %s =%s 2> /dev/null" % (wavfile, start, end)
    #print(cmd)
    print(text)
    os.system(cmd)
    time.sleep(0.3)
    

