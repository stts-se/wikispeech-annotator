#!/usr/bin/env python3

import sys, json
import typer
from fastapi import FastAPI

from time import time

#export LD_PRELOAD=/opt/intel/mkl/lib/intel64/libmkl_def.so:/opt/intel/mkl/lib/intel64/libmkl_avx2.so:/opt/intel/mkl/lib/intel64/libmkl_core.so:/opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so:/opt/intel/mkl/lib/intel64/libmkl_intel_thread.so:/opt/intel/lib/intel64_lin/libiomp5.so
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/harald/git/kaldi/src/lib:/home/harald/git/kaldi/tools/openfst/lib


sys.path.insert(0, "/home/harald/git/py-kaldi-asr/build/lib.linux-x86_64-3.8/")
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder


class kaldi_asr:
    def __init__(self, language):
        if language == "eng":
            self.MODELDIR    = '/media/bigdisk/kaldi_models/english/kaldi-generic-en-tdnn_fl-r20190609'
        elif language == "gle":
            self.MODELDIR = '/media/bigdisk/kaldi_models/irish/dist_test/hb_20_10_97'
        else:
            raise ValueError("Unsupported language: %s" % language)

        print('%s loading model...' % self.MODELDIR)
        time_start = time()
        self.kaldi_model = KaldiNNet3OnlineModel (self.MODELDIR)
        print('%s loading model... done, took %fs.' % (self.MODELDIR, time()-time_start))



        
    def decode_wavfile(self, wavfile):
        print('%s creating decoder...' % self.MODELDIR)
        time_start = time()
        decoder = KaldiNNet3OnlineDecoder (self.kaldi_model)
        print('%s creating decoder... done, took %fs.' % (self.MODELDIR, time()-time_start))

        print('decoding %s...' % wavfile)
        time_start = time()
        if decoder.decode_wav_file(wavfile):
            print('%s decoding worked!' % self.MODELDIR)

            decoded_string,likelihood = decoder.get_decoded_string()
            print("decoded_string: %s\nlikelihood: %s" % (decoded_string,likelihood))

            #HBtime_scale = 0.01
            time_scale = 0.03
            words, times, lengths = decoder.get_word_alignment()

            print("** word alignment: :")
            for i, word in enumerate(words):
                print('**   %f\t%f\t%s' % (time_scale * float(times[i]), time_scale*float(times[i] + lengths[i]), word))


        else:
            print('%s decoding did not work :(' % self.MODELDIR)

        print("%s decoding took %8.2fs" % (self.MODELDIR, time() - time_start ))
        return decoded_string

    def decode(self):
        pass

    def finalize(self):
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




asr = kaldi_asr("eng")


@app.get("/asr/{language}")
@cliapp.command()
def decode_wavfile(language: str, audio: str):
    result = asr.decode_wavfile(audio)

    
    #asr.decode(audio)
    #result = asr.finalize()
    
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
