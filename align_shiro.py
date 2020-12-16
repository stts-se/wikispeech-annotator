import sys, os, glob, re, json

import typer
from fastapi import FastAPI

cliapp = typer.Typer()
state = {
    "verbose": False,
    "shiropath": "../SHIRO"
}


app = FastAPI()


@app.get("/")
@cliapp.command()
def hello():
    message = typer.style("hello", fg="green")
    typer.echo(message)
    return "hello"


def runCmd(cmd):
    debug(cmd)
    retval = os.system(cmd)
    debug(retval)
    return retval

def debug(msg):
    if state["verbose"]:
        sys.stderr.write(str(msg))
        sys.stderr.write("\n")
    
def ensureExistsDir(*args):
    for directory in args:
        if not os.path.exists(directory):
            os.mkdir(directory)
    

@app.get("/make_def/")
@cliapp.command()
def make_def(csvfile: str, modeldir: str):
    #lua shiro-mkpm.lua examples/arpabet-phoneset.csv \
    #    -s 3 -S 3 > phonemap.json
    #lua shiro-pm2md.lua phonemap.json \
    #    -d 12 > modeldef.json    
    ensureExistsDir(modeldir)

    
    phonemap_cmd = "lua %s/shiro-mkpm.lua %s -s 3 -S 3 > %s/phonemap.json" % (state["shiropath"], csvfile, modeldir)
    runCmd(phonemap_cmd)
    
    modeldef_cmd = "lua %s/shiro-pm2md.lua %s/phonemap.json -d 12 > %s/modeldef.json" % (state["shiropath"], modeldir, modeldir)
    runCmd(modeldef_cmd)

@app.get("/make_index/")
@cliapp.command()
def make_index_from_xml(wavdir: str, xmldir: str, aligndir: str, addPauBetweenWords=True):
    ensureExistsDir(aligndir)
    indexfile = "%s/index.csv" % aligndir
    index = []
    for xmlfile in sorted(glob.glob("%s/*.xml" % xmldir)):
        m = re.match("^.*/([^/.]+).xml$", xmlfile)
        base = m.group(1)
        last_added = ""
        print(base)
        if os.path.exists("%s/%s.wav" % (wavdir, base)):
            trans = []
            with open(xmlfile) as fh:
                lines = fh.readlines()
            for line in lines:                                
                if addPauBetweenWords:
                    wm = re.match('<word input_string="([^"]+)"', line)
                    if wm:
                        #word = wm.group(1)
                        #if word not in ["SILENCE_TOKEN", ",", "?", "'", "."]:
                        if not last_added in ["sil", "pau"]:
                            trans.append("pau")
                    
                m = re.match('<phoneme symbol="([^"]+)"/>', line)
                if m:
                    symbol = m.group(1)
                    if addPauBetweenWords:
                        if symbol != "sil":
                            trans.append(symbol)
                    else:
                        trans.append(symbol)
                if len(trans) > 0:
                    last_added = trans[-1]
        out = "%s,%s" % (base, " ".join(trans))
        index.append(out)
    with open(indexfile, "w") as fh:
        fh.write("%s" % "\n".join(index)) 

@app.get("/make_word_index/")
@cliapp.command()
def make_word_index_from_xml(wavdir: str, xmldir: str, aligndir: str):
    if not os.path.exists(aligndir):
        os.mkdir(aligndir)
    index = []
    indexfile = "%s/word_index.csv" % aligndir
    for xmlfile in sorted(glob.glob("%s/*.xml" % xmldir)):
        m = re.match("^.*/([^/.]+).xml$", xmlfile)
        base = m.group(1)
        #print(base)
        if os.path.exists("%s/%s.wav" % (wavdir, base)):
            words = []
            word = False
            with open(xmlfile) as fh:
                lines = fh.readlines()
            for line in lines:
                wm = re.match('<word input_string="([^"]+)"', line)
                pm = re.match('<phoneme symbol="([^"]+)"/>', line)
                if wm:
                    if word and not word.endswith("sil"):
                        words.append(word)
                    word = wm.group(1)
                    if word == "SILENCE_TOKEN":
                        word = "sil"
                    if word == ",":
                        word = "sil"
                    if " " in word:
                        word = word.replace(" ", "+")
                if pm:
                    symbol = pm.group(1)
                    word += " "+symbol
            #last word..        
            words.append(word)
            #print(words)
            out = "%s, %s" % (base, ", ".join(words))
            index.append(out)
    with open(indexfile, "w") as fh:
        fh.write("%s" % "\n".join(index)) 




@app.get("/make_index_from_labs/")
@cliapp.command()
def make_index_from_labs(wavdir: str, labdir: str, aligndir: str):
    ensureExistsDir(aligndir)
    indexfile = "%s/index.csv" % aligndir
    index = []
    for labfile in sorted(glob.glob("%s/*.lab" % labdir)):
        m = re.match("^.*/([^/.]+).lab$", labfile)
        base = m.group(1)
        debug(base)
        if os.path.exists("%s/%s.wav" % (wavdir, base)):
            trans = []
            with open(labfile, encoding="latin-1") as fh:
                lines = fh.readlines()
            for line in lines:                                
                symbol = line.split(" ")[2].strip()
                trans.append(symbol)
        out = "%s,%s" % (base, " ".join(trans))
        index.append(out)
    with open(indexfile, "w") as fh:
        fh.write("%s" % "\n".join(index)) 

@app.get("/make_word_index_from_labs/")
@cliapp.command()
def make_word_index_from_labs(wavdir: str, labdir: str, aligndir: str):
    ensureExistsDir(aligndir)
    indexfile = "%s/word_index.csv" % aligndir
    index = []
    for labfile in sorted(glob.glob("%s/*.lab" % labdir)):
        m = re.match("^.*/([^/.]+).lab$", labfile)
        base = m.group(1)
        debug(base)
        wordlabfile = "%s/%s.ord" % (labdir, base)
        if os.path.exists("%s/%s.wav" % (wavdir, base)):
            wordtranses = []
            trans = []
            with open(labfile, encoding="latin-1") as fh:
                lines = fh.readlines()
            with open(wordlabfile, encoding="latin-1") as fh:
                wordlines = fh.readlines()
            s = 0
            w = 0
            while s < len(lines):
                line = lines[s]
                start, end, symbol = line.strip().split(" ")
                trans.append(symbol)
                s += 1

                if w < len(wordlines):
                    wordline = wordlines[w]
                    wordstart, wordend, word = wordline.strip().split(" ")
                else:
                    wordend = end
                    word = "<silence>"
                    
                debug("%s %s" % (word, symbol))

                if wordend == end:
                    w += 1
                    wordtrans = "%s %s" % (word, " ".join(trans))
                    wordtranses.append(wordtrans)
                    trans = []
                
        out = "%s,%s" % (base, ", ".join(wordtranses))
        index.append(out)
    with open(indexfile, "w") as fh:
        fh.write("%s" % "\n".join(index)) 




        
@app.get("/feats/")
@cliapp.command()
def feats(wavdir: str, aligndir: str):
    #lua shiro-fextr.lua index.csv \
    #-d "../cmu_us_bdl_arctic/orig/" \
    #-x ./extractors/extractor-xxcc-mfcc12-da-16k -r 16000    
    ensureExistsDir(aligndir)
    featsdir = "%s/feats" % aligndir
    ensureExistsDir(featsdir)
    indexfile = "%s/index.csv" % aligndir

    if state["verbose"]:
        quiet = ""
    else:
        quiet = "> /dev/null"
        
    cmd = "lua %s/shiro-fextr.lua %s -d \"%s\" -x %s/extractors/extractor-xxcc-mfcc12-da-16k -r 16000 %s" % (state["shiropath"],indexfile, wavdir, state["shiropath"], quiet)
    #print(cmd)
    runCmd(cmd)

    cmd2 = "mv %s/*.param %s" % (wavdir, featsdir)
    runCmd(cmd2)
    cmd3 = "mv %s/*.raw %s" % (wavdir, featsdir)
    runCmd(cmd3)


    
@app.get("/train/")
@cliapp.command()
def train(modeldir: str, featsdir: str, indexfile: str, sil: bool=False):
    # Train a model given speech and phoneme transcription

    # (Assuming feature extraction has been done.)

    # First step: create an empty model.

    # ./shiro-mkhsmm -c modeldef.json > empty.hsmm
    cmd1 = "%s/shiro-mkhsmm -c %s/modeldef.json > %s/empty.hsmm" % (state["shiropath"], modeldir, modeldir)
    runCmd(cmd1)
    
    # Second step: initialize the model (flat start initialization scheme).

    # lua shiro-mkseg.lua index.csv \
    #   -m phonemap.json \
    #   -d "../cmu_us_bdl_arctic/orig/" \
    #   -e .param -n 36 -L sil -R sil > unaligned-segmentation.json
    # ./shiro-init \
    #   -m empty.hsmm \
    #   -s unaligned-segmentation.json \
    #   -FT > flat.hsmm

    addsil = ""
    if sil:
        addsil = "-L sil -R sil"

    cmd2 = "lua %s/shiro-mkseg.lua %s -m %s/phonemap.json -d %s -e .param -n 36 %s > %s/unaligned-segmentation.json" % (state["shiropath"], indexfile, modeldir, featsdir, addsil, modeldir)
    runCmd(cmd2)

    cmd3 = "%s/shiro-init -m %s/empty.hsmm -s %s/unaligned-segmentation.json -FT > %s/flat.hsmm" % (state["shiropath"], modeldir, modeldir, modeldir)
    runCmd(cmd3)


    
    # Third step: bootstrap/pre-train using the HMM training algorithm and update the alignment accordingly.

    # ./shiro-rest \
    #   -m flat.hsmm \
    #   -s unaligned-segmentation.json \
    #   -n 5 -g > markovian.hsmm
    # ./shiro-align \
    #   -m markovian.hsmm \
    #   -s unaligned-segmentation.json \
    #   -g > markovian-segmentation.json

    cmd4 = "%s/shiro-rest -m %s/flat.hsmm -s %s/unaligned-segmentation.json -n 5 -g > %s/markovian.hsmm" % (state["shiropath"], modeldir, modeldir, modeldir)
    runCmd(cmd4)
    
    cmd5 = "%s/shiro-align -m %s/markovian.hsmm -s %s/unaligned-segmentation.json -g > %s/markovian-segmentation.json" % (state["shiropath"], modeldir, modeldir, modeldir)
    runCmd(cmd5)

    # Final step: train the model using the HSMM training algorithm.

    # ./shiro-rest \
    #   -m markovian.hsmm \
    #   -s markovian-segmentation.json \
    #   -n 5 -p 10 -d 50 > trained.hsmm

    cmd6 = "%s/shiro-rest -m %s/markovian.hsmm -s %s/markovian-segmentation.json -n 5 -p 10 -d 50 > %s/trained-model.hsmm" % (state["shiropath"], modeldir, modeldir, modeldir)
    runCmd(cmd6)


@app.get("/align_feats/")
@cliapp.command()
def align_feats(modeldir: str, featsdir: str, aligndir: str, indexfile: str, sil=False):
    # Second step: create a dummy segmentation from the index file.
    
    # lua shiro-mkseg.lua index.csv \
    #   -m phonemap.json \
    #   -d "../cmu_us_bdl_arctic/orig/" \
    #   -e .param -n 36 -L sil -R sil > unaligned.json

    ensureExistsDir(aligndir)

    addsil = ""
    if sil:
        addsil = "-L sil -R sil"

        
    cmd1 = "lua %s/shiro-mkseg.lua %s -m %s/phonemap.json -d %s -e .param -n 36 %s > %s/unaligned.json" % (state["shiropath"], indexfile, modeldir, featsdir, addsil, aligndir)
    runCmd(cmd1)

    
    # Third step: since the search space for HSMM is an order of magnitude larger than HMM, it's more efficient to start from a HMM-based forced alignment, then refine the alignment using HSMM in a pruned search space. When running HSMM training, SHIRO applies such pruning by default. You may need to increase the search space (-p 10 -d 50) a bit to avoid alignment errors caused by a narrowed search space, although this will make it run slower. A rule of thumb on choosing p is to multiply the average number of states in a file by 0.1. For example, if on average an audio file contains 30 phonemes and each phoneme has 5 states, p should be 30 * 5 * 0.1 = 15. If you're doing alignment straight from HSMM, the factor would be around 0.2.

    # ./shiro-align \
    #   -m trained-model.hsmm \
    #   -s unaligned.json \
    #   -g > initial-alignment.json
    # ./shiro-align \
    #   -m trained-model.hsmm \
    #   -s initial-alignment.json \
    #   -p 10 -d 50 > refined-alignment.json    

    cmd2 = "%s/shiro-align -m %s/trained-model.hsmm -s %s/unaligned.json -g > %s/initial-alignment.json" % (state["shiropath"], modeldir, aligndir, aligndir)
    runCmd(cmd2)

    #TODO compute p based on calculation in comment above
    p = "100"
    
    cmd3 = "%s/shiro-align -m %s/trained-model.hsmm -s %s/initial-alignment.json -p %s -d 50 > %s/refined-alignment.json" % (state["shiropath"], modeldir, aligndir, p, aligndir)
    runCmd(cmd3)


@app.get("/labs/")
@cliapp.command()
def labs(aligndir: str, labdir: str):
    with open("%s/refined-alignment.json" % aligndir) as fh:
        alignments = json.load(fh)

    ensureExistsDir(labdir)

    timefactor = 0.005
    
    for item in alignments["file_list"]:
        m = re.match("^.*/([^/.]+).param", item["filename"])
        base = m.group(1)
        debug(base)
        lab = []
        starttime = 0
        for state in item["states"]:
            if state["ext"][1] == 2:
                endtime = state["time"]*timefactor
                symbol = state["ext"][0]
                lab.append("%.2f %.2f %s" % (starttime, endtime, symbol))
                starttime = endtime
        with open("%s/%s.lab" % (labdir, base), "w") as fh:
            fh.write("\n".join(lab))
                
@app.get("/word_labs/")
@cliapp.command()
def word_labs(aligndir: str, labdir: str, sil: bool=False):
    ensureExistsDir(labdir)
    windex = {}
    with open("%s/word_index.csv" % aligndir) as fh:
        lines = fh.readlines()
        for line in lines:
            info = line.split(",")
            base = info[0]
            windex[base] = []
            if sil:
                windex[base] = [("sil", ["sil"])]
            for wordtrans in info[1:]:
                wordtranslist = wordtrans.strip().split(" ")
                word = wordtranslist[0]
                trans = wordtranslist[1:]
                windex[base].append((word, trans))
            if sil:
                windex[base].append(("sil", ["sil"]))

    with open("%s/refined-alignment.json" % aligndir) as fh:
        alignments = json.load(fh)


    timefactor = 0.005
    
    for item in alignments["file_list"]:
        m = re.match("^.*/([^/.]+).param", item["filename"])
        base = m.group(1)
        debug(base)
        lab = []
        wlab = []
        starttime = 0
        w = 0
        i = 0
        wstart = 0
        #print(windex[base])
        (word, trans) = windex[base][w]
        #print(word, trans)
        for state in item["states"]:
            if state["ext"][1] == 2:
                endtime = state["time"]*timefactor
                symbol = state["ext"][0]
                wsymbol = trans[i]
                debug("%d\t%d\t%s\t%s" % (i, state["time"], symbol, wsymbol))

                if symbol == "pau" and wsymbol != "sil":
                    if w > 0:
                        print("INSERTED PAUSE in %s at %s: %s" % (base, word, wsymbol))
                    wlabline = "%.2f %.2f %s" % (wstart, endtime, symbol)
                    wlab.append(wlabline)
                    wstart = endtime
                    continue
                    
                if symbol == "pau" and wsymbol == "sil":
                    pass
                elif symbol != wsymbol:
                    print("MISMATCH: %s\t%s" % (symbol, wsymbol))
                    sys.exit()
                lab.append("%s %s %s" % (starttime, endtime, symbol))
                starttime = endtime
                i += 1
                if i == len(trans):
                    wlabline = "%.2f %.2f %s" % (wstart, endtime, word)
                    #print(wlabline)
                    wlab.append(wlabline)
                    w += 1
                    if w < len(windex[base]):
                        i = 0
                        (word, trans) = windex[base][w]
                        wstart = endtime

                #print(wlab)
        #sys.exit()
        with open("%s/%s.lab" % (labdir, base), "w") as fh:
            fh.write("\n".join(wlab))
                
            
@app.get("/align/")
@cliapp.command()
def align(modeldir: str, aligndir: str, wavdir: str, sil: bool=False):
    ensureExistsDir(aligndir)

    indexfile = "%s/index.csv" % aligndir
    #make_index_from_lab(wavdir, labdir, indexfile)
    featsdir = "%s/feats" % aligndir
    feats(wavdir, aligndir)
    align_feats(modeldir, featsdir, aligndir, indexfile, sil)
    labdir = "%s/lab" % aligndir
    labs(aligndir, labdir)
    wordlabdir = "%s/wordlab" % aligndir
    word_labs(aligndir, wordlabdir, sil)

@app.get("/align_file/")
@cliapp.command()
def align_file(modeldir: str, wavfile: str, transcription: str, sil: bool=False):

    if os.path.exists(transcription):
        with open(transcription) as fh:
            transcription = fh.read().strip()

    #NOTE
    #The phoneme "ax" causes segmentation fault, temporarily replacing it with "ah"
    transcription = transcription.replace("ax", "ah")

            
    
    aligndir = "/tmp/shiro_align"
    ensureExistsDir(aligndir)

    indexfile = "%s/index.csv" % aligndir
    base = os.path.basename(wavfile).split(".")[0]
    with open(indexfile, "w") as fh:
        fh.write("%s,%s\n" % (base, transcription))            

    wavdir = "%s/wav/" % aligndir
    ensureExistsDir(wavdir)
    featsdir = "%s/feats/" % aligndir

    cmd = "cp %s %s" % (wavfile, wavdir)
    #print(cmd)
    os.system(cmd)

    feats(wavdir, aligndir)
    align_feats(modeldir, featsdir, aligndir, indexfile, sil)
    labdir = "%s/lab" % aligndir
    labs(aligndir, labdir)
    #wordlabdir = "%s/wordlab" % aligndir
    #word_labs(aligndir, wordlabdir, sil)
    with open("%s/%s.lab" % (labdir, base)) as fh:
        lab = fh.read()
        print(lab)
    return lab.split("\n")

@app.get("/word_align_file/")
@cliapp.command()
def word_align_file(modeldir: str, wavfile: str, wordtranscription: str, sil: bool=False):

    aligndir = "/tmp/shiro_align"
    ensureExistsDir(aligndir)

    translist = []
    for wordtrans in wordtranscription.split(","):
        word = wordtrans.strip().split(" ")[0]
        trans = wordtrans.strip().split(" ")[1:]
        translist.extend(trans)
    transcription = " ".join(translist)

    #print(transcription)
    
    base = os.path.basename(wavfile).split(".")[0]

    indexfile = "%s/index.csv" % aligndir
    with open(indexfile, "w") as fh:
        fh.write("%s,%s\n" % (base, transcription))            

    wordindexfile = "%s/word_index.csv" % aligndir
    with open(wordindexfile, "w") as fh:
        fh.write("%s,%s\n" % (base, wordtranscription))            

    wavdir = "%s/wav/" % aligndir
    ensureExistsDir(wavdir)
    featsdir = "%s/feats/" % aligndir

    cmd = "cp %s %s" % (wavfile, wavdir)
    #print(cmd)
    os.system(cmd)

    feats(wavdir, aligndir)
    align_feats(modeldir, featsdir, aligndir, indexfile, sil)
    #labdir = "%s/lab" % aligndir
    #labs(aligndir, labdir)
    wordlabdir = "%s/wordlab" % aligndir
    word_labs(aligndir, wordlabdir, sil)
    with open("%s/%s.lab" % (wordlabdir, base)) as fh:
        lab = fh.read()
        print(lab)
    return lab.split("\n")
        
@cliapp.callback()
def main(
        verbose: bool = typer.Option(False,"--verbose","-v"),
        shiropath: str = typer.Option("../SHIRO","--shiropath","-sp")):
    """
    Add annotations to sound.
    """
    if verbose:
        message = typer.style("Will write verbose output", fg="red")
        typer.echo(message)
        state["verbose"] = True
    state["shiropath"] = shiropath


if __name__ == "__main__":
    cliapp()
    
