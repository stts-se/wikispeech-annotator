Simple word alignment using aeneas.

Install aeneas:

    https://github.com/readbeyond/aeneas

    Install Python3, FFmpeg, and eSpeak

    Make sure the following executables can be called from your shell: espeak, ffmpeg, ffprobe, pip, and python

    First install numpy with pip and then aeneas (this order is important):

    python3 -m pip install numpy
    python3 -m pip install aeneas==1.7.0

    (There seems to be a problem with timing in versions after 1.7.0)

    To check whether you installed aeneas correctly, run:

    python -m aeneas.diagnostics





Run alignment script, arguments: language iso 3-letter, wavfile (16 kHz mono), textfile

python3 aeneas_word_aligner.py eng word_align_tests/eng01.wav word_align_tests/eng01.txt > word_align_tests/eng01_out.lab
python3 aeneas_word_aligner.py swe word_align_tests/swe01.wav word_align_tests/swe01.txt > word_align_tests/swe01_out.lab
python3 aeneas_word_aligner.py gle word_align_tests/gle01.wav word_align_tests/gle01.txt > word_align_tests/gle01_out.lab



Listen to the soundfile with 0.3 s gap between segments:

python3 play_lab_with_silence_between_segments.py word_align_tests/gle01.wav word_align_tests/gle01_out.lab

Create a soundfile with 1 s gap between segments:

python3 make_wav_with_silence_between_segments.py word_align_tests/swe01.wav word_align_tests/swe01_out.lab word_align_tests/swe01_out.wav
