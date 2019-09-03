#!/usr/bin/env python
#-*- coding:utf-8 -*- 
# Author: Joven Chu
# Email: jovenchu@gmail.com
# Time: 2019-09-02 15:31:45
# Project: resume_analysis
# About: 面试问题库的es上传

import csv
import jieba
#from __future__ import print_function
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch import helpers
jieba.load_userdict("ElasticSearch_for_Match/code/new/usedict.txt")
csvfile = open("all_qa.csv", encoding = 'utf-8')
f = csv.reader(csvfile)
dataset = []
num = 0
for line in f:
    data = []
    num+=1
    quest = line[1].strip().replace(" ","")
    q_type = line[-1].strip().replace(" ","")
    seg_list = jieba.cut(quest, cut_all=False)
    quest_sp = " ".join(seg_list)
    data.append(quest_sp)
    data.append(quest)
    data.append(q_type)
    dataset.append(data)
    
es_hosts = ["127.0.0.1:9200"]
body = []
for i in range(len(dataset)):
    body.append({
        "_index": "resume_question",
        "_type": "artice",
        "_id": i + 1,
        "_source": {
              "sp_quest": dataset[i][0],
              "quest":dataset[i][1],
               "q_type":dataset[i][2]
        }
        })

def main():
    es = Elasticsearch(es_hosts)
    helpers.bulk(es, body)
    res = es.search(index='resume_question', body={"query": {"match_all": {}}})
    pprint(res)


if __name__ == '__main__':
    main()
