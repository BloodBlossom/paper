import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import os
import re
from googletrans import Translator

from bibtexparser import bibdatabase
year_start = 2016
year_end = 2021
fields = [
    "AI",
    "NIS",
    "SSS"    
]
db = BibDatabase()
db.entries=[]
translator = Translator(service_urls=['translate.google.cn'])
for field in fields:
    for year in range(year_start,year_end):
        current_dir = "bibtex/{}/{}".format(field,year)
        for bibtex_file_name in os.listdir(current_dir):
            print(field,year,bibtex_file_name)
            db.entries = []
            with open(current_dir+'/'+bibtex_file_name) as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
            # print(bibtex_file_name,len(bib_database.entries))
            bibtexs = bib_database.entries
            for index in range(len(bibtexs)):
                # |interpretability Robustness 
                res = re.compile(r'(.|\n)*(interpretability)+(.|\n)*',re.I).search(bibtexs[index]["title"])
                if res != None:
                    title_cn = translator.translate(bibtexs[index]["title"],dest="zh-CN").text
                    bibtexs[index]["title_cn"]=title_cn

                    db.entries.append(bibtexs[index])
            if len(db.entries) != 0:
                output = "filter_interpretability/{}/{}/{}".format(field,year,bibtex_file_name)
                writer = BibTexWriter()
                with open(output, 'w') as bibfile:
                    bibfile.write(writer.write(db))
                    

        
