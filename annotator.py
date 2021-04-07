#!/usr/bin/env python3

import sys, os, json
import typer
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum
from tempfile import TemporaryFile, mkstemp
import base64

from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc

#import align_shiro
import fleep

import validator






class aeneas_aligner:
    def __init__(self, language):
        config = TaskConfiguration()
        if not language in Language.CODE_TO_HUMAN:
            print("Language %s not supported for alignment" % language)
            print(
                "Supported languages are:\n%s" % "\n".join(Language.CODE_TO_HUMAN_LIST)
            )
            sys.exit()


        config[gc.PPN_TASK_LANGUAGE] = language
        config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
        #set boundary in middle of silence
        config[gc.PPN_TASK_ADJUST_BOUNDARY_ALGORITHM] = "percent"
        config[gc.PPN_TASK_ADJUST_BOUNDARY_PERCENT_VALUE] = 50
        self.task = Task()
        self.task.configuration = config

    def run(self, audio_file, text_file):
        self.task.audio_file_path_absolute = audio_file
        self.task.text_file_path_absolute = text_file

        ExecuteTask(self.task).execute()

        alignment = []
        for fragment in self.task.sync_map_leaves():
            if not fragment.text == "":
                alignment.append(
                    {
                        "start": int(float(fragment.begin) * 1000),
                        "end": int(float(fragment.end) * 1000),
                        "text": fragment.text,
                    }
                )
        return alignment

def iso2aeneas_language_code(isocode):
    map = {
        "sv-SE":"swe",
        "en-GB":"eng"
    }
    return map[isocode] 


def getTmpFile(data, ext="", binary=False):
    (_, filename) = mkstemp(suffix=ext)
    #print(filename)

    mode =  "w"
    if binary:
        mode = "wb"
    
    with open(filename, mode) as fh:
        fh.write(data)
    return filename

def rmTmpFile(filename):
    os.remove(filename)


cliapp = typer.Typer()
state = {"verbose": False}


app = FastAPI()
templates = Jinja2Templates(directory="templates")


class AlignMethod(str, Enum):
    AENEAS = "AENEAS"
    SHIRO = "SHIRO"
    JSON_SHIRO = "JSON_SHIRO"

    
class AudioInputType(str, Enum):
    BASE64 = "BASE64"
    FILE = "FILE"
    URL = "URL"

class TextInputType(str, Enum):
    STRING = "STRING"
    FILE = "FILE"
    URL = "URL"

class AudioInputFormat(str, Enum):
    PCM = "PCM"
    MP3 = "MP3"
    OGG = "OGG"

class ReturnType(str, Enum):
    JSON = "JSON"
    HTML = "HTML"
    LAB = "LAB"
    
class AlignRequest(BaseModel):
    alignMethod: AlignMethod = AlignMethod.AENEAS
    audioInputType: AudioInputType = AudioInputType.BASE64
    audioInputFormat: AudioInputFormat = AudioInputFormat.PCM
    textInputType: TextInputType = TextInputType.STRING
    language: str = None #HB trying w None
    text: str = None #HB trying w None
    audioInput: str
    returnType: ReturnType = ReturnType.JSON

@app.get("/")
@cliapp.command()
def hello():
    message = typer.style("hello", fg="green")
    typer.echo(message)
    return "hello"


@app.get("/align/{language}")
@cliapp.command()
def align(language: str, soundfile: str, textfile: str):
    #HB TODO build areq and run "post" command (like vad and validate)
    aeneas = aeneas_aligner(language)
    alignment = aeneas.run(soundfile, textfile)

    data = {
        "sound_file": soundfile,
        "text_file": textfile,
        "language": language,
        "alignment": alignment,
    }

    typer.echo(json.dumps(data, indent=4))
    if state["verbose"]:
        message = typer.style("verbose", fg="red")
        typer.echo(message)
    return data




@app.get("/vad")
@cliapp.command()
def vad(soundfile: str, audioInputType: str = AudioInputType.FILE, returnType: str = ReturnType.JSON):
    areq = AlignRequest(audioInput=soundfile, audioInputType=audioInputType, returnType=returnType)
    result = vad(areq)
    if returnType == ReturnType.JSON:
        typer.echo(json.dumps(result, indent=4))
    else:
        print(result.body.decode())
    return result


    
@app.post("/vad")
def vad(areq: AlignRequest):
    if areq.audioInputType == AudioInputType.FILE and areq.audioInputFormat == AudioInputFormat.PCM:
        audiofile = areq.audioInput
    elif areq.audioInputType == AudioInputType.BASE64 and areq.audioInputFormat == AudioInputFormat.PCM:
        tmpaudio = getTmpFile(base64.b64decode(areq.audioInput), ".wav", True)
        audiofile = tmpaudio
    elif areq.audioInputType == AudioInputType.FILE and areq.audioInputFormat == AudioInputFormat.MP3:
        audiofile = areq.audioInput
        (_, tmpaudio) = mkstemp(suffix=".wav")
        #HB TODO remove system calls
        cmd = f"sox {audiofile} -c 1 -r 16000 {tmpaudio}"
        print(cmd)
        os.system(cmd)
        audiofile = tmpaudio
    else:
        #TODO: URL should be supported (by requests) or removed
        raise HTTPException(status_code=422, detail=f"audioInputType {areq.audioInputType} not yet supported")


    vad_timepoints = validator.getVadTimepoints(audiofile)
    

    
    data = {
        "vad": vad_timepoints,
    }

    
    if areq.returnType == ReturnType.JSON:
        return data
    elif areq.returnType == ReturnType.LAB:
        lab = list()
        for item in vad_timepoints:
            lab.append(f'{item["start"]} {item["end"]} {item["text"]}')
        data = "\n".join(lab)
        return Response(content=data, media_type="text/plain")

    


@app.post("/align")
def align(request: Request, areq: AlignRequest):

    if areq.audioInputType == "FILE":
        audiofile = areq.audioInput
    elif areq.audioInputType == "BASE64":
        tmpaudio = getTmpFile(base64.b64decode(areq.audioInput), ".wav", True)
        audiofile = tmpaudio
    else:
        #TODO: URL should be supported (by requests) or removed
        raise HTTPException(status_code=422, detail=f"audioInputType {areq.audioInputType} not yet supported")

        
    if areq.textInputType == "FILE":
        textfile = areq.text
    elif areq.textInputType == "STRING":
        tmptxt = getTmpFile(areq.text, ".txt")
        textfile = tmptxt
    else:
        #TODO: URL should be supported (by requests) or removed        
        raise HTTPException(status_code=422, detail=f"textInputType {areq.textInputType} not yet supported")

    
    if areq.alignMethod == AlignMethod.AENEAS:
        alignment = aeneas_align(areq.language, audiofile, textfile)
    elif  areq.alignMethod == AlignMethod.SHIRO:
        alignment = shiro_align(areq.language, audiofile, textfile)
    elif  areq.alignMethod == AlignMethod.JSON_SHIRO:
        alignment = shiro_align_json(areq.language, audiofile, textfile)

    
    if areq.audioInputType == "BASE64":
        rmTmpFile(tmpaudio)
    if areq.textInputType == "STRING":        
        rmTmpFile(tmptxt)


    data = {
        "alignment": alignment,
    }

    if areq.returnType == ReturnType.JSON:
        return data
    elif areq.returnType == ReturnType.HTML:
        newtokens = []
        for token in alignment:
            token["dur"] = token["end"]-token["start"]
            token["startS"] = token["start"]/1000
            token["durS"] = token["dur"]/1000
            newtokens.append(token)

        if areq.audioInputType == AudioInputType.BASE64:
            audio_src = "data:audio/wav;base64,"+areq.audioInput
        else:
            audio_src = areq.audioInput
            #print(audio_src)
            
        return templates.TemplateResponse("output.html", {"request": request, "audio_src": audio_src, "tokens": newtokens})
        #return render_template("output.html", audio_data=are.audioInput, tokens=newtokens)
    elif areq.returnType == ReturnType.LAB:
        lab = list()
        for item in alignment:
            start = round(item["start"]/1000, 2)
            end = round(item["end"]/1000, 2)
            lab.append(f'{start} {end} {item["text"]}')
        data = "\n".join(lab)
        return Response(content=data, media_type="text/plain")
        


    
def aeneas_align(language, audiofile, textfile):
    aeneas = aeneas_aligner(iso2aeneas_language_code(language))    
    alignment = aeneas.run(audiofile, textfile)
    return alignment



shiro_models = {
    "en-GB": "aligner_models/nnc_en",
    "sv-SE": "aligner_models/hb_sv"
}
    

def shiro_align(language, audiofile, textfile):
    modeldir = shiro_models[language] 
    sil = True
    with open(textfile) as fh:
        transcription = fh.read()
    
    alignment = align_shiro.align_file(modeldir, audiofile, transcription, sil)
    return alignment

def shiro_align_json1(language, audiofile, textfile):
    modeldir = shiro_models[language] 
    sil = True
    with open(textfile) as fh:
        jsontext = json.loads(fh.read())
        print(jsontext)
    to_shiro = []
    for w in jsontext["text"]:
        word = w["word"]
        phones = " ".join(w["phones"])
        to_shiro.append(f"{word} {phones}")
    transcription = ", ".join(to_shiro)
    print(transcription)
    alignment = align_shiro.word_align_file(modeldir, audiofile, transcription, sil)
    return alignment

def shiro_align_json(language, audiofile, textfile):
    modeldir = shiro_models[language] 
    sil = True
    with open(textfile) as fh:
        jsontext = json.loads(fh.read())
        #print(jsontext)
    to_shiro = []
    for w in jsontext["text"]:
        phones = " ".join(w["phones"])
        to_shiro.append(phones)
    transcription = " ".join(to_shiro)
    #print(transcription)
    alignment = []
    labels = align_shiro.align_file(modeldir, audiofile, transcription, sil)

    i = 0
    words = []

    #Add first silence
    if sil == True:
        (start, end, symbol) = labels[0].split()
        words = [{"word": symbol, "start": start, "end": end, "phones": [{"start":start, "end": end, "symbol": symbol}]}]
        i = 1

    #Add start end end times for each word and phone
    for w in jsontext["text"]:
        word = w["word"]
        phones = w["phones"]
        phonelabels = labels[i:i+len(phones)]
        i += len(phones)
        phones = []
        wordstart = phonelabels[0].split()[0]
        wordend = phonelabels[-1].split()[1]
        for lab in phonelabels:
            (start, end, symbol) = lab.split()
            phones.append({"start": start, "end": end, "symbol": symbol})
        words.append({"word": word, "start": wordstart, "end": wordend, "phones": phones})

    #Add last silence
    if sil == True:
        (start, end, symbol) = labels[-1].split()
        words.append({"word": symbol, "start": start, "end": end, "phones": [{"start":start, "end": end, "symbol": symbol}]})

    alignment = {"text": words}
            
    return alignment


@app.get("/validate")
@cliapp.command()
def validate(soundfile: str, audioInputType: str = AudioInputType.FILE, jsonfile: str = None, language: str = None ):
    areq = AlignRequest(audioInput=soundfile, audioInputType=audioInputType)
    result = validate(areq)
    typer.echo(json.dumps(result, indent=4))
    return result


@app.post("/validate")
def validate(areq: AlignRequest):
    vals = []
    val_msgs = []

    #1) Format should be wav, mp3, ogg (opus) and match specified format in areq
    vals.append(validate_audio_format(areq))

    #2) Audio should contain speech
    vals.append(validate_audio_contains_speech(areq))

    score = getValScore(vals)
    return {
        "score": f"{score:.2f}",
        "validation": vals
    }


def getValScore(vals):
    if vals == []:
        return 1
    total = 0
    for val in vals:
        total += val["validation"]
    score = total/len(vals)
    return score

def validate_audio_format(areq):
    if areq.audioInputType == "FILE":
        audiofile = areq.audioInput
        val = checkAudioFormat(audiofile, areq.audioInputFormat)
    elif areq.audioInputType == "BASE64":
        tmpaudio = getTmpFile(base64.b64decode(areq.audioInput), ".wav", True)
        audiofile = tmpaudio
        val = checkAudioFormat(audiofile, areq.audioInputFormat)
        
    else:
        #TODO: URL should be supported (by requests) or removed
        raise HTTPException(status_code=422, detail=f"audioInputType {areq.audioInputType} not yet supported")
    return val
    
def checkAudioFormat(audiofile, audioFormat):

    fleep_map = {
        "audio/wav": "PCM",
        "audio/mp3": "MP3"
    }

    with open(audiofile, "rb") as file:
        info = fleep.get(file.read(128))
        fleep_format = info.mime[0]
    if fleep_map[fleep_format] == audioFormat:        
        val_msg = "Audio format OK"
        val = 1
    else:
        val_msg = f"Audio format: fleep format: {fleep_format}, audioInputFormat: {audioFormat}"
        val = 0
    return {
        "source": "checkAudioFormat",
        "validation": val,
        "message": val_msg
    }


def validate_audio_contains_speech(areq):
    if areq.audioInputType == "FILE":
        audiofile = areq.audioInput
    elif areq.audioInputType == "BASE64":
        tmpaudio = getTmpFile(base64.b64decode(areq.audioInput), ".wav", True)
        audiofile = tmpaudio
    val = checkAudioContainsSpeech(audiofile, areq.audioInputFormat)
    return val

def checkAudioContainsSpeech(wavfile, audioFormat):    
    if validator.voice_activity_detection(wavfile):
        val_msg = "Audio contains speech: OK"
        val = 1
    else:
        val_msg = "Audio appears not to contain speech"
        val = 0
    return {
        "source": "checkAudioContainsSpeech",
        "validation": val,
        "message": val_msg
    }
        

@cliapp.callback()
def main(verbose: bool = typer.Option(False,"--verbose","-v")):
    """
    Add annotations to sound.
    """
    if verbose:
        message = typer.style("Will write verbose output", fg="red")
        typer.echo(message)
        state["verbose"] = True


if __name__ == "__main__":
    cliapp()
