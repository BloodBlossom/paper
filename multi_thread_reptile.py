#爬取dblp上会议论文的bibtex引用
#修改lib
#修改year_start和year_end限制年份
#当前测试同时爬取三次会议没有问题

import queue
import threading
from time import thread_time_ns
import requests
import re
import os
import time
import random
from threading import Thread
from multiprocessing import Array, Process
from queue import Empty, Queue
from requests.sessions import Request, session

lib = {
        # "AAAI": {
        #     "AAAI":"aaai",
        #     "SafeAI@AAAI":"safeai"
        # },
        # "NeurlPS":{
        #     "NeurlPS":"nips",
        # },
        # "ACL":{
        #     "ACL":"acl",
        # },
        # "CVPR":{
        #     "CVPR":"cvpr",
        # },
        # "ICCV":{
        #     "ICCV":"iccv",
        # }, 
        # "ICML":{
        #     "ICML":"icml",
        # },
        # "IJCAI":{ 
        #     "IJCAI":"ijcai",
        # },

        # "CCS":{
        #     "CCS":"ccs"
        # },
        # "USENIX":{
        #     "USENIX":"uss"
        # },
        # "S&P":{
        #     "S&P":"sp"
        # },
        # "EUROCRYPT":{
        #     "EUROCRYPT":"eurocrypt"
        # },
        # "CRYPTO":{
        #     "CRYPTO":"crypto"
        # }, 
         
        # "PLDI":{
        #     "PLDI":"pldi",
        #     "MADL":"mdl"
        
        # },
        # "POPL":{
        #     "POPL":"popl"
        # },
        # "FSE/ESEC":{
        #     "FSE/ESEC":"sigsoft",
        #     "FSE":"fse"
        # },
        # "SOSP":{
        #     "SOSP":"sosp"
        # },
        # "OOPSLA":{
        #     "OOPSLA":"oopsla",
        #     "ONWARD@OOPSLA":"onward"
        # },
        # "ICSE":{
        #     "ICSE":"icse",
        # },
        # "ISSTA":{
        #     "ISSTA":"issta"
        # },
        # "OSDI":{
        #     "OSDI":"osdi"
        # },
        "KBSE":{
            "KBSE":"kbse",
            "ASE":"ase"
        },        
    }



def producer(url,out_q,headers,cookies,session,pid):
    print("Producer",pid,url)
    res = requests.Response()
    data=b""
    try:
        res = session.get(url,headers=headers,cookies=cookies,timeout=100.05)
        if(res.status_code == 429):
            print("Producer",pid,"429 error")
    except requests.exceptions.ReadTimeout as e:
        print("Producer",pid,"Read Timeout")
    except requests.exceptions.ConnectTimeout as e:
        print("Producer",pid,"Connect Timeout")
    except requests.exceptions.ConnectionError as e:
        print("Producer",pid,"Connection Error")
    data = res.content
    bibtex_urls = re.compile(r'https://dblp\.org/rec/conf/[a-zA-Z0-9/.]{1,30}\?view=bibtex').findall(data.decode())
    bibtex_urls = list(set(bibtex_urls))
    for bibtex_url in bibtex_urls:
        # print("Producer",pid,"bibtex_url",bibtex_url)
        out_q.put(bibtex_url)

def consumer(in_q,out_q,headers,cookies,session,pid):
    t = threading.currentThread()
    while  True :
        # print("consumer",in_q.queue,out_q.queue)
        time.sleep(random.random()*2)
        url = in_q.get()
        res = requests.Response()
        data = b""
        print("Consumer",pid,t.ident,url)
        try:
            res = session.get(url, headers=headers, cookies=cookies,timeout=9.05)
            if(res.status_code == 429):
                in_q.put(url)
                in_q.task_done()
                print("Consumer wait",int(res.headers["Retry-After"]))
                time.sleep(int(res.headers["Retry-After"]))
                continue
            data = res.content
        except requests.exceptions.ReadTimeout as e:
            print("Consumer",pid,t.ident,"Timeout and Retry")
            in_q.put(url)
            in_q.task_done()
            continue
        except requests.exceptions.ConnectTimeout as e:
            print("Consumer",pid,t.ident,"Connect Timeout and Retry")
            in_q.put(url)
            in_q.task_done()
            continue
        except requests.exceptions.ConnectionError as e:
            print("Consumer",pid,t.ident,"Connection Error and Retry")
            in_q.put(url)
            in_q.task_done()
            continue
        
       
        # print(data.decode())
        # assert res.status_code == 200

        try:
            bibtex = re.compile(r'@[in]*proceedings{.*}', re.S).findall(data.decode())[0]
            # print(bibtex)
            # print(in_q.queue)
            out_q.put(bibtex)
            in_q.task_done()
            print("Consumer",pid,t.ident,res.status_code,in_q.unfinished_tasks)
        except Exception as e:
            print(res.status_code,e)



def process_conference(url,output,year):
    pid = os.getpid()
    print("Process",pid,url)
    session = requests.Session()
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
           "Cache-Control": "max-age=0", 
           "Upgrade-Insecure-Requests": "1",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",     
           "Referer": "https://dblp.org/search", 
           "Connection": "close",
           "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
           "Accept-Encoding": "gzip, deflate"}

    cookies = {"dblp-search-mode": "c", "dblp-dismiss-new-feature-2019-08-19": "3"}
    
    #保存识别出的bibtex页面链接
    record_thread_consumer = []

    queue_path = Queue()
    queue_bibtex = Queue()

    thread_producer = Thread(target=producer,args=(url,queue_path,headers,cookies,session,pid))
    thread_producer.start()
    for i in range(5):
        thread_consumer = Thread(target=consumer,args=(queue_path,queue_bibtex,headers,cookies,session,pid))
        thread_consumer.start()
        record_thread_consumer.append(thread_consumer)
    
    thread_producer.join()
    print("Process",pid,"producer end")
    queue_path.join()
    print("Process",pid,"consumer end")
    
    results = '\n'.join(queue_bibtex.queue)
    # print(results)
    with open('bibtex/SSS/{}/{}'.format(year,output),"w") as f:
        f.write(results)


if __name__ == '__main__':
    record_process = []

    year_start = 2016
    year_end = 2021

    for year in range(year_start,year_end):
        for key_1 in lib.keys():
            for key_2 in lib[key_1].keys():
                main_name = lib[key_1][key_1]
                sub_name = lib[key_1][key_2]
                output = "{key}_{year}.bib".format(key=key_2,year=year)
                url = "https://dblp.org/db/conf/{main_name}/{sub_name}{year}.html".format(main_name=main_name,sub_name=sub_name, year=year)
                
                # 多进程，并行处理不同的会议
                process = Process(target=process_conference,args=(url,output,year))
                process.daemon = True
                process.start()
                record_process.append(process)

    for process in record_process :
        process.join()