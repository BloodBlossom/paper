from re import match
import bibtexparser
import re
with open('test.bib') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)
print(bib_database.entries)
# for i in range(len(bib_database.entries)):
#     res = re.compile(r'(.|\n)*(Biological\sSimulation|security|interpretability)+(.|\n)*').search(bib_database.entries[i]["title"])
#     print(res.group())