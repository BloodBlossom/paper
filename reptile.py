import requests
import re

session = requests.Session()

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
           "Cache-Control": "max-age=0", 
           "Upgrade-Insecure-Requests": "1",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",     
           "Referer": "https://dblp.org/search?q=AAAI", 
           "Connection": "close",
           "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
           "Accept-Encoding": "gzip, deflate"}
cookies = {"dblp-search-mode": "c", "dblp-dismiss-new-feature-2019-08-19": "3"}

lib = {
    # "NDSS": 'ndss',
    # "CCS": 'ccs',
    # "S&P": 'sp',
    # "Usenix_Security": "uss"
    "AAAI": "aaai"
}


def get_all_bibtex(url):
    bibtexs = []
    res = session.get(url, headers=headers, cookies=cookies)
    data = res.content
    assert res.status_code == 200
    bibtex_urls = re.compile(r'https://dblp\.org/rec/conf/[a-zA-Z0-9/.]{1,20}\?view=bibtex').findall(data.decode())
    bibtex_urls = list(set(bibtex_urls))
    for l in bibtex_urls:
        bibtex = get_one_bibtex(l)
        bibtexs.append(bibtex)
    bibtexs = list(set(bibtexs))
    return bibtexs


def get_one_bibtex(url):
    res = session.get(url, headers=headers, cookies=cookies)
    data = res.content
    assert res.status_code == 200
    try:
        bibtex = re.compile(r'@[in]*proceedings{.*}', re.S).findall(data.decode())[0]
        print(bibtex)
        return bibtex
    except Exception as e:
        print(e)
        # print(data)
    return '{}:error!'.format(url)

def main():
    # year = 2020
    # key = 'NDSS'
    # name = lib[key]
    year_start = 2020
    year_end = 2021
    for year in range(year_start, year_end):
        for key in lib:
            name = lib[key]
            output = "{key}_{year}.bibtex".format(key=key, year=year)
            url = "https://dblp.org/db/conf/{name}/{name}{year}.html".format(name=name, year=year)
            results = get_all_bibtex(url)
            tmp = '\n'.join(results)
            with open('bibtex/{}'.format(output), 'w') as f:
                f.write(tmp)

if __name__ == '__main__':
    main()
