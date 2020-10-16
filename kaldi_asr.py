#!/usr/bin/env python3

import sys, json
import typer
from fastapi import FastAPI

from time import time
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder


class kaldi_asr:
    def __init__(language):
        if language == "eng":
            MODELDIR    = '/opt/kaldi/model/kaldi-generic-en-tdnn_f-r20190609'
        else:
            raise ValueError("Unsupported language: %s" % language)

        print('%s loading model...' % MODELDIR)
        time_start = time()
        kaldi_model = KaldiNNet3OnlineModel (MODELDIR)
        print('%s loading model... done, took %fs.' % (MODELDIR, time()-time_start))

        print('%s creating decoder...' % MODELDIR)
        time_start = time()
        self.decoder = KaldiNNet3OnlineDecoder (kaldi_model)
        print('%s creating decoder... done, took %fs.' % (MODELDIR, time()-time_start))


        
    def decode():
        pass

    def finalize():
        pass



cliapp = typer.Typer()
state = {"verbose": False}


app = FastAPI()


@app.get("/")
@cliapp.command()
def hello():
    message = typer.style("hello", fg="green")
    typer.echo(message)
    return "hello"


@app.get("/asr/{language}")
@cliapp.command()
def decode(language: str, audio: bytes):
    asr = kaldi_asr(language)
    asr.decode(audio)
    result = asr.finalize()
    
    data = {
        "result": result,
    }

    typer.echo(json.dumps(data, indent=4))
    if state["verbose"]:
        message = typer.style("verbose", fg="red")
        typer.echo(message)
    return data


@cliapp.callback()
def main(verbose: bool = False):
    """
    Add annotations to sound.
    """
    if verbose:
        typer.echo("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    cliapp()
