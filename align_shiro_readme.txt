To create phonemap from abair xml:
cat ../abair-gitea/abair-corpora/cmg_ga_mu_corpusbeag/textproc_xml/*.xml | egrep 'symbol=".+"' | sed 's/<phoneme symbol="//g' | sed 's/"\/>//g' | sort | uniq > irish_test/gle_sampa.csv


To build model and align, with word and segments labs:


python align_shiro.py make-def irish_test/gle_sampa.csv llf_test/
python align_shiro.py make-index-from-xml llf_test/wav/ llf_test/textproc_xml/ llf_test/align
python align_shiro.py make-word-index-from-xml llf_test/wav/ llf_test/textproc_xml/ llf_test/align
python align_shiro.py feats llf_test/wav/ llf_test/align
python align_shiro.py train llf_test llf_test/align/feats llf_test/align/index.csv
python align_shiro.py align-feats llf_test llf_test/align/feats/ llf_test/align llf_test/align/index.csv
python align_shiro.py labs llf_test/align llf_test/lab
python align_shiro.py word-labs llf_test/align llf_test/wordlab

