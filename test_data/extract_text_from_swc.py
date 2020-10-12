import sys
from lxml import etree


xmlfile = sys.argv[1]
tree = etree.parse(xmlfile)

#Includes <ignore>
#paragraphs = tree.xpath("//p")

#Skips ignore
paragraphs = tree.xpath("/article/d/p")

for par in paragraphs:
    sentences = par.xpath("s")
    for sent in sentences:
        #print(etree.tostring(sent, method="text"))
        #print(etree.tostring(sent))
        tokens = sent.xpath("t")
        tlist = []
        for token in tokens:
            tlist.append(token.text)
            if token.tail:
                tlist.append(token.tail)
        print("".join(tlist))
    print("")

