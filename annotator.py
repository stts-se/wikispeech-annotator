#!/usr/bin/env python3

import sys, os, json
import typer
from fastapi import FastAPI
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

from validator import *

class aeneas_aligner:
    def __init__(self, language):
        config = TaskConfiguration()
        if not language in Language.CODE_TO_HUMAN:
            print("Language %s not supported for alignment" % language)
            print(
                "Supported languages are:\n%s" % "\n".join(Language.CODE_TO_HUMAN_LIST)
            )
            sys.exit()
            #return "ERROR"

        config[gc.PPN_TASK_LANGUAGE] = language
        config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
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

class AlignMethod(str, Enum):
    AENEAS = "AENEAS"
    SHIRO = "SHIRO"

    
class AudioInputType(str, Enum):
    BASE64 = "BASE64"
    URL = "URL"

class AudioInputFormat(str, Enum):
    PCM = "PCM"
    MP3 = "MP3"
    OGG = "OGG"
    
class AlignRequest(BaseModel):
    alignMethod: AlignMethod = "AENEAS"
    audioInputType: AudioInputType = "BASE64"
    audioInputFormat: AudioInputFormat = "PCM"
    language: str
    text: str
    audioInput: str


@app.get("/")
@cliapp.command()
def hello():
    message = typer.style("hello", fg="green")
    typer.echo(message)
    return "hello"


@app.get("/align/{language}")
@cliapp.command()
def align(language: str, soundfile: str, textfile: str):
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

@app.post("/align")
def align(areq: AlignRequest):

    if areq.alignMethod == AlignMethod.AENEAS:
        return aeneas_align(areq)
    elif  areq.alignMethod == AlignMethod.SHIRO:
        return shiro_align(areq)

def aeneas_align(areq):
    aeneas = aeneas_aligner(iso2aeneas_language_code(areq.language))

    if areq.audioInputType == "URL":
        alignment = aeneas.run(areq.audioInput, areq.text)
    elif areq.audioInputType == "BASE64":
        tmpaudio = getTmpFile(base64.b64decode(areq.audioInput), ".wav", True)
        tmptxt = getTmpFile(areq.text, ".txt")
        alignment = aeneas.run(tmpaudio, tmptxt)
        rmTmpFile(tmpaudio)
        rmTmpFile(tmptxt)

    data = {
        "alignment": alignment,
    }

    #typer.echo(json.dumps(data, indent=4))
    if state["verbose"]:
        message = typer.style("verbose", fg="red")
        typer.echo(message)
    return data

def shiro_align(areq):
    import align_shiro

    modeldir = "aligner_models/nnc_en"
    sil = True
    wavfile = areq.audioInput
    transcription = areq.text
    
    alignment = align_shiro.align_file(modeldir, wavfile, transcription, sil)
    data = {
        "alignment": alignment,
    }
    return data

@app.get("/validate/{language}")
@cliapp.command()
def validate(language: str, soundfile: str, jsonfile: str):
    v = validator(verbose=state["verbose"])

    with open(jsonfile) as fh:
        data = json.load(fh)
    
    result = v.run(soundfile, data)

    typer.echo(json.dumps(result, indent=4))
    return result


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
