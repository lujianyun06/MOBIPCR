#coding=utf-8

from pymongo import MongoClient
from constants import DB_NAME
from core2 import extract_features
import multiprocessing
import sys
import os

DATA_TYPE = None


def call_and_add(fname,ngram_num):
    global DATA_TYPE
    try:
        print '[*] Feature Extracting: {}'.format(fname)
        result = extract_features(fname,ngram_num)
        print '[*] Adding to db: {}'.format(fname)
        client = MongoClient()
        db = client[DB_NAME]
        result['data_type'] = DATA_TYPE
        db['apk'].update({'sha256': result['sha256']}, result, upsert=True)
        #os.remove(fname)
    except Exception as e:
        print '[!] Error occured with {}, {}'.format(fname, e)

def perform_analysis(d, t,ngram_num):
    global DATA_TYPE
    DATA_TYPE = t
    file_names = []
    index = 0
    for root, dirs, files in os.walk(d):
        for name in files:
            file_name = os.path.join(root, name)
            if not file_name.endswith(".apk"):
                continue
            file_names.append(file_name)
            call_and_add(file_name,ngram_num)
            #add record
            record_file = open('add_db_record.txt', 'a')
            record_file.write(str(index+1) + "  "+t+": "+name+"\n")
            record_file.close
            
            index += 1
            print '[','*'*40,'] already process',index

if __name__ == '__main__':
    if len(sys.argv) > 2:
        #single path
        dir_path = sys.argv[1]
        data_type = sys.argv[2]
        ngram_num = int(sys.argv[3])
        if data_type not in ('goodware','malware'):
            print '[+] You should use goodware or malware as data type'
        else:
            perform_analysis(dir_path,data_type,ngram_num)
    else:
        print '[+] Usage: python {} <dir_path> <data_type>'.format(__file__)
