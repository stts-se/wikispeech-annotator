#!/usr/bin/env python3

from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task
from aeneas.task import TaskConfiguration
from aeneas.textfile import TextFileFormat
import aeneas.globalconstants as gc


class aeneas_aligner:
    def __init__(self, language):
        
        # create Task object
        config = TaskConfiguration()

        #config[gc.PPN_TASK_LANGUAGE] = Language.ENG
        if not language in Language.CODE_TO_HUMAN:
            print("Language %s not supported for alignment" % language)
            print("Supported languages are:\n%s" % "\n".join(Language.CODE_TO_HUMAN_LIST))
            sys.exit()
            
        config[gc.PPN_TASK_LANGUAGE] = language
        config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = TextFileFormat.PLAIN
        self.task = Task()
        self.task.configuration = config


    def run(self, audio_file, text_file):
        
        #task.audio_file_path_absolute = u"test_data/shakespeare_part1.wav"
        #task.text_file_path_absolute = u"test_data/shakespeare_part1.txt"
        self.task.audio_file_path_absolute = audio_file
        self.task.text_file_path_absolute = text_file

        # process Task
        ExecuteTask(self.task).execute()

        # print produced sync map
        #print(task)
        #print(dir(task))
        #print(task.sync_map)
        #print(task.text_file)
        alignment = []
        for fragment in self.task.sync_map_leaves():
            if not fragment.text == "":
                #print("%d %d %s" % (fragment.begin*1000, fragment.end*1000, fragment.text))
                alignment.append(
                    {"start":int(float(fragment.begin)*1000),
                     "end":int(float(fragment.end)*1000),
                     "text":fragment.text
                    }
                )
        return alignment


import sys
import argparse, typer
import json

#parser = argparse.ArgumentParser(description='Add annotations to sound.')
#parser.add_argument('language', metavar="language", type=str, help='Language to use for alignment')
#parser.add_argument('soundfile', metavar="soundfile", type=str, help='Soundfile to align')
#parser.add_argument('textfile', metavar="textfile", type=str, help='textfile to align')
#
#args = parser.parse_args()
#
#language = args.language
#soundfile = args.soundfile
#textfile = args.textfile

app = typer.Typer()
state = {"verbose":False}

@app.command()
def hello():
    message = typer.style("hello",fg="green")
    typer.echo(message)
    


@app.command()
def align(language: str, soundfile: str, textfile: str):
    aeneas = aeneas_aligner(language)
    alignment = aeneas.run(soundfile, textfile)

    data = {
        "sound_file": soundfile,
        "text_file": textfile,
        "language": language,
        "alignment": alignment
    }

    #print(json.dumps(data,indent=4))
    typer.echo(json.dumps(data,indent=4))
    if state["verbose"]:
        message = typer.style("verbose",fg="red")
        typer.echo(message)
        

@app.callback()
def main(verbose: bool = False):
    """
    Add annotations to sound.
    """
    if verbose:
        typer.echo("Will write verbose output")
        state["verbose"] = True    

if __name__ == "__main__":
    #typer.run(main)
    app()
