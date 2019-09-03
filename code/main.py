#!/usr/bin/env python
#-*- coding:utf-8 -*- 
# Author: Joven Chu
# Email: jovenchu@gmail.com
# Time: 2019-09-02 16:35:46
# Project: resume_analysis
# About: 面试问题的es查询及api部署

import csv
import json
import jieba
#from __future__ import print_function
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from flask import Flask, request, render_template
jieba.load_userdict("ElasticSearch_for_Match/code/new/usedict.txt")

app = Flask(__name__) 


def get_stop(path):
    stop_list = []
    f  = open(path, 'r')
    for line in f:
        if line.strip()=="":
            continue
        stop_list.append(line.strip())
    return stop_list

def remove_stop(seg_list,stop_list, syn_dict):
    corpus = []
    for i in seg_list:
        if i not in stop_list:
            if i in syn_dict:
                corpus.append(syn_dict[i])
            else:
                corpus.append(i)
    return corpus

def jieba_cut(sp_q):
    cq = []
    sq_list = jieba.cut(sp_q, cut_all = False)
    for i in sq_list:
        cq.append(i)
    return cq

def re_ans(q, sp_q):
    """
    获取答案
    q: 面试问题
    sp_q:精准分割后的问题
    """
    result = {}
    es_hosts = ["127.0.0.1:9200"]
    es = Elasticsearch(es_hosts)
    # 进行匹配获取答案
    res = es.search(index='resume_question',body={"query": {"match": {"sp_quest": sp_q}}})
    if res["hits"]["max_score"] <2 or res["hits"]["max_score"]==None:
        res = es.search(index='resume_question',body={"query": {"match": {"quest": q}}})

    num = 0
    ans = res["hits"]["hits"]
    for i in ans:
        num += 1
        reply = {}
        reply["quest"] = i["_source"]["quest"]
        reply["q_type"] = i["_source"]["q_type"].replace(' ','')
        reply["score"] = i["_score"]
        result[num] = reply
        # if num >4 or i["_score"]<2:
        #     break
    result = json.dumps(result, ensure_ascii=False)
    return result
def main(q):
    #2.加载停用词词表
    print(q)
    path = "./cibiao.txt"
    sy_path = "./syn.json"
    f = open(sy_path, "r")
    stop_list = get_stop(path)
    syn_dict = json.load(f)
    #3.回答问题
    #3.1. 进行数据处理(分词，去停止词)
    seg_list = jieba.cut(q, cut_all = False)
    corpus = remove_stop(seg_list,stop_list, syn_dict)
    #3.2.1 分字匹配
    sp_q = "".join(corpus)
    cq = jieba_cut(sp_q)
    # 3.3对问题分割处理
    #3.3.1 分词匹配
    q = " ".join(cq)
    print(q)
    result = re_ans(q, sp_q)
    return result 
@app.route('/')
def get_tasks():
    # q = request.args.get('q')
    q = '团队合作能力'
    result = main(q)
    print(result)
    return result


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='192.168.1.109', port="8234")
