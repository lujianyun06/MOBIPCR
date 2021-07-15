# -*- coding: utf-8 -*-

from __future__ import division
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import VMAnalysis
from androguard.decompiler.decompiler import DecompilerDAD
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis import analysis
from androguard.core.bytecodes import dvm
from constants import SPECIAL_STRINGS, DB_REGEX, API_CALLS, PERMISSIONS,NGRAM_THRE, VULNERABILITY
import hashlib
import math
from collections import Counter
import cPickle as pickle
import test_vul
import sys
import os
import core2
from multiprocessing import Pool
from threading import Thread
from multiprocessing import Process
import multiprocessing
import math


result = {}
result['feature_vectors'] = {}

def callback_combine(wrap):
    global result
    if wrap[0] != None:
        tag_1st = wrap[0]
        value_1st = wrap[1]
        result[tag_1st] = value_1st
    if wrap[2] != None:
        tag_2rd = wrap[2]
        value_2rd = wrap[3]
        result['feature_vectors'][tag_2rd] = value_2rd

def print_error(value):
    print("error: ", value)


def get_opcodes(d):
    print("get_opcodes")
    result ={}
    result['feature_vectors'] = {}
    opt_seq = []
    ngram_num = 2
    for m in d.get_methods():
        for i in m.get_instructions():
            #in order to save space ,we store opcode instead of the name of optcode
            #opt_seq.append(i.get_name())
            #i.OP equals to i.get_op_value(), it's a decimal. we need transform it to hexdigest using hex method
            #like 84 in decimal is 0x54 in hex, and we need to cut the common string '0x' off using slice method
            opt_seq.append(str(hex(i.get_op_value()))[2:].zfill(2))
    print '*'*30,'NGRAM:',ngram_num
    optngramlist = [tuple(opt_seq[i:i+ngram_num]) for i in xrange(len(opt_seq) - ngram_num+1)]
    optngram = Counter(optngramlist)
    optcodes = dict()
    tmpCodes = dict(optngram)
    for k,v in optngram.iteritems():
        if v>=NGRAM_THRE:
            optcodes[str(k)] = v
    result['feature_vectors']['opt_codes'] = optcodes
    print("opt_codes get compeleted")
    wrap =[]
    wrap.append(None)
    wrap.append(None)
    wrap.append('opt_codes')
    wrap.append(optcodes)
    return wrap


def get_permissions(a):
    print("get_permissions")
    result ={}
    result['feature_vectors'] = {}
    result['permissions'] = a.get_permissions()
    result['feature_vectors']['permissions'] = []
    for permission in PERMISSIONS:
        if permission in result['permissions']:
            result['feature_vectors']['permissions'].append(permission)
    print("permissions get compeleted")
    wrap =[]
    wrap.append('permissions')
    wrap.append(result['permissions'])
    wrap.append('permissions')
    wrap.append(result['feature_vectors']['permissions'])
    print('permissions')
    return wrap  

def get_api(dx):
    print("get_api")
    result ={}
    result['feature_vectors'] = {}
    result['feature_vectors']['api_calls'] = []
    for call in API_CALLS:
        if dx.tainted_packages.search_methods(".", call, "."):
            result['feature_vectors']['api_calls'].append(call) 
    print("api get compeleted")
    wrap =[]
    wrap.append(None)
    wrap.append(None)
    wrap.append('api_calls')
    wrap.append(result['feature_vectors']['api_calls'])
    return wrap 

     

def get_vul(file_path):
    print("get_vul")
    result ={}
    result['feature_vectors'] = {}
    result['feature_vectors']['vulnerability'] = []
    apk_vul = test_vul.get_vul(file_path)
    result['vulnerability'] = apk_vul
    for vul in VULNERABILITY:
        if vul in apk_vul:
            result['feature_vectors']['vulnerability'].append(vul)
    print("vul get compeleted")
    wrap =[]
    wrap.append('vulnerability')
    wrap.append(result['vulnerability'])
    wrap.append('vulnerability')
    wrap.append(result['feature_vectors']['vulnerability'])
    return wrap 



def extract_features(file_path):    
    try:
        a = APK(file_path)
        d = DalvikVMFormat(a.get_dex())
        dx = VMAnalysis(d)
        d.set_vmanalysis(dx)
        d.set_decompiler(DecompilerDAD(d, dx))
    except:
        print('can not parse this app, Internal error')
        return None
    # result['sha256'] = hashlib.sha256(a.get_raw()).hexdigest()
    global result
    #multi process
    task_cnt = 4
    pool = Pool(task_cnt)
    for i in range(task_cnt):
        if i==0:
            pool.apply_async(func=get_opcodes, args=(d,), callback=callback_combine)
        elif i==1:
            pool.apply_async(func=get_permissions, args=(a,), callback=callback_combine)
        elif i==2:
            pool.apply_async(func=get_api, args=(dx,), callback=callback_combine)
        elif i==3:
            pool.apply_async(func=get_vul, args=(file_path,), callback=callback_combine)

    pool.close()
    pool.join()
    if 'permissions' not in result['feature_vectors']:
        callback_combine(get_permissions(a))
    if 'api_calls' not in result['feature_vectors']:
        callback_combine(get_api(dx))
    if 'vulnerability' not in result['feature_vectors']:
        callback_combine(get_vul(file_path))
    if 'opt_codes' not in result['feature_vectors']:
        callback_combine(get_opcodes(d))
    return result



def  get_single_strvec(file_name):
    features = extract_features(file_name)
    cur_file_path = os.path.split(os.path.realpath(__file__))[0] + '/'
    final_features = pickle.load(open(cur_file_path + 'final_feature_obj.p', 'rb'))
    permission_list = final_features['permission']
    api_list = final_features['api']
    vul_list = final_features['vul']
    opts_list = final_features['opts']
    feature_str = ''
    for permission in final_features['permission']:
        value = 0
        if permission in features['feature_vectors']['permissions']:
            value = 1
        feature_str = feature_str + str(value) + '$'
    for api in final_features['api']:
        value = 0
        if api in features['feature_vectors']['api_calls']:
            value = 1
        feature_str = feature_str + str(value) + '$'
    for vul in final_features['vul']:
        value = 0
        if vul in features['feature_vectors']['vulnerability']:
            value = 1
        feature_str = feature_str + str(value) + '$'        
    for i in xrange(len(final_features['opts'])):
        value = 0
        if final_features['opts'][i] in features['feature_vectors']['opt_codes']:
            value = 1
        feature_str = feature_str + str(value) + '$'
    return feature_str

def get_single_vec(file_name):
    #全面分析
    ss = get_single_strvec(file_name)[:-1]
    result = [int(x) for x in ss.strip().split('$')]

    return result

    
    
