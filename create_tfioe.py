
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import numpy as np
import sys
import os
import pickle
import math

client = MongoClient()
db = client["bishe"]

GOOD_TYPE="goodware"
BAD_TYPE="malware"

selected_len = 30000
optunits_postfix = "opt_units"

def create_tfidf(cur_type):
    reverse_type = ""
    if cur_type == GOOD_TYPE:
        reverse_type = BAD_TYPE
    else:
        reverse_type = GOOD_TYPE
    opt_units = pickle.load(open(cur_type+optunits_postfix))
    reverse_units = pickle.load(open(reverse_type+optunits_postfix))
    selected_opts = open(cur_type+"selected_opts.p","a+")
    index = 0
    for appid, cur_unit in opt_units.items():
        app_res = {}
        
        total_cnt = cur_unit["total_cnt"]
        index = index + 1
        selected_opts.write(appid + "  " + str(index) + "\n")
        for code, count in cur_unit["opt_map"].items():
            tf = float(count)/float(total_cnt)
            ioe = get_ioe(code, reverse_units)
            res = tf * ioe
            app_res[code]=res
        d_order=sorted(app_res.items(),key=lambda x:x[1],reverse=True)
        for key_score in d_order[:selected_len]:
            selected_opts.write(key_score[0] +"#"+str(key_score[1]) + "\n")
    selected_opts.close()
                 

def get_ioe(code, reverse_units):
    reverse_size = len(reverse_units)
    contains_size = 0
    
    for appid, cur_unit in reverse_units.items():
        if cur_unit["opt_map"].has_key(code):
            contains_size = contains_size+1

    
    ioe = math.log(float(reverse_size)/float((contains_size+1)), 10)  
    return ioe
    
if __name__ == "__main__":
   create_tfidf(BAD_TYPE)
   create_tfidf(GOOD_TYPE)
    
    
  
