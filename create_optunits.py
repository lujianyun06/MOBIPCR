
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from core2 import extract_features
from sklearn.feature_extraction.text import CountVectorizer   
from sklearn.feature_extraction.text import TfidfTransformer  
import numpy as np
import sys
import os
import pickle
import math

client = MongoClient()
db = client["bishe"]

GOOD_TYPE="goodware"
BAD_TYPE="malware"

def create_opt_units(data_type, limit=200000):
    opt_units = {}
    i = 0
    for apk in db.apk.find():
        if(apk["data_type"]!=data_type):
            continue
        if(i>limit):
            break
        i = i+1
        opt_units[apk['sha256']] = {}
        opt_total_count = 0
        opt_units[apk['sha256']]
        opt_units[apk['sha256']]["opt_map"] = {}
        index = 0
        for codes ,v in apk['feature_vectors']["opt_codes"].iteritems():
            cnt = int(v)
            index = index + 1
            
            opt_units[apk['sha256']]["opt_map"][codes] = cnt
            opt_total_count = opt_total_count+cnt
        opt_units[apk['sha256']]["total_cnt"]=opt_total_count
    pickle.dump(opt_units, open(data_type + "opt_units", "wb"))

if __name__ == "__main__":
     #create_opt_units(BAD_TYPE)
     
     create_opt_units(GOOD_TYPE, 200000)
     
    
    
    
