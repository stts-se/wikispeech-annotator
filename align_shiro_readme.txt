To create phonemap from abair xml:
cat ../abair-gitea/abair-corpora/cmg_ga_mu_corpusbeag/textproc_xml/*.xml | egrep 'symbol=".+"' | sed 's/<phoneme symbol="//g' | sed 's/"\/>//g' | sort | uniq > irish_test/gle_sampa.csv


The phonelist csv file has to be utf-8


To build model and align, with word and segments labs:


python align_shiro.py make-def irish_test/gle_sampa.csv llf_test/
python align_shiro.py make-index-from-xml llf_test/wav/ llf_test/textproc_xml/ llf_test/align
python align_shiro.py make-word-index-from-xml llf_test/wav/ llf_test/textproc_xml/ llf_test/align
python align_shiro.py feats llf_test/wav/ llf_test/align
python align_shiro.py train llf_test llf_test/align/feats llf_test/align/index.csv
python align_shiro.py align-feats llf_test llf_test/align/feats/ llf_test/align llf_test/align/index.csv
python align_shiro.py labs llf_test/align llf_test/lab
python align_shiro.py word-labs llf_test/align llf_test/wordlab




python3 align_shiro.py align-file test_data/nnc/model/ test_data/nnc/wav/nnc_arctic_0033.wav "hh iy ah n f ow l d ah d ah l ao ng t ay p r ih t ah n l eh t er sil ah n d hh ae n d ah d ih t t uw g r eh g s ah n" --sil


python3 align_shiro.py word-align-file test_data/nnc/model/ test_data/nnc/wav/nnc_arctic_0033.wav "He hh iy, unfolded ah n f ow l d ah d, a ah, long l ao ng, typewritten t ay p r ih t ah n, letter l eh t er, sil sil, and ah n d, handed hh ae n d ah d, it ih t, to t uw, Gregson g r eh g s ah n" --sil
