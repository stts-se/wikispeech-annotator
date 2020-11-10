#!/usr/bin/env python3

import sys, json
import typer
from fastapi import FastAPI



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




cliapp = typer.Typer()
state = {"verbose": False}


app = FastAPI()


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
