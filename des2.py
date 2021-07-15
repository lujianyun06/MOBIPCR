# -*- coding: utf-8 -*-

from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import VMAnalysis
from androguard.decompiler.decompiler import DecompilerDAD
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis import analysis
from androguard.core.bytecodes import dvm
from selected_constants import API_CALLS, PERMISSIONS, VULNERABILITY,OPTION_CODES
import hashlib
import math
from collections import Counter
import cPickle as pickle
import test_vul
import sys
import numpy as np  
import os
import vector_getter
from util4predict import tag_constant
import time
from multiprocessing import Pool
from threading import Thread
from multiprocessing import Process
import multiprocessing
import math


# Extract all features for a given application

NEIGHBOR_NUM = 5000

clf_map = {}


neighbor_result = []

data_list = []

tag_list = tag_constant.tag_list

FIRST_LEVEL_COUNT = 3

ngram_num = 2


stacking_filepath = './stacking_file/'

def load_models():
    modelPath = './final_models/'
    for tag in tag_list:
        clf = pickle.load( open( modelPath + "train_data_" + tag + ".p", "rb" ))
        print(tag + ' load completed')
        clf_map[tag] = clf
    print( len(clf_map))

def mk_stackingfile_dir():
    if not os.path.exists(stacking_filepath):
        os.makedirs(stacking_filepath)


def process(file_path=None, target_vec=None):
    if not file_path == None:
        target_vec = get_feature_vector(file_path)
    elif not target_vec==None:
        pass
    else:
        raise Exception('You must specify a file path or provide a feature vector to be measured')
    global data_list

    time1 = time.time()

    index_sum_map = calculate_distance_multiprocess(target_vec)
    time2 = time.time()
    selected_data_list, selected_index_list = choose_neighbors(index_sum_map, data_list, target_vec)
    time3 = time.time()
    clf_tag,clf_choose_score = choose_clf(selected_data_list, selected_index_list)
    time4 = time.time()
    return get_stacking_file(target_vec, clf_tag, selected_data_list,clf_choose_score)


def get_feature_vector(file_path):
    print('Calculate the eigenvector of APK to be predicted...')
    vec = vector_getter.get_single_vec(file_path)
    print('The eigenvector is done')
    return vec

def calculate_distance(target_vec):
    index_sum_map = dict()

    target_vec = [int(x) for x in target_vec]
    vec_len = len(target_vec)
    for i, v in enumerate(data_list):
        sample_vec = v[:-1]
        if not len(sample_vec) == len(target_vec):
            print("The length is inconsistent, and the generated app vector has an error")
            print('len1=' + str(len(sample_vec)) + ' len2=' + str(len(target_vec)))
            return
        sum_vec = list(sample_vec[i] + target_vec[i] for i in range(vec_len))
        diff_count = str(sum_vec).count('1')
        value_sum = vec_len - diff_count
        index_sum_map[i] = value_sum
    return index_sum_map  
g_index_map = dict()

def callback_appenddict(index_map):
    pass
    global g_index_map
    g_index_map.update(index_map)


def calculate_part(target_vec, datalist, offset):
    index_map = dict()
    vec_len = len(target_vec)
    for i, v in enumerate(datalist):
        sample_vec = v[:-1]
        if not len(sample_vec) == len(target_vec):
            print("The length is inconsistent, and the generated app vector has an error")
            print('len1=' + str(len(sample_vec)) + ' len2=' + str(len(target_vec)))
            return
        sum_vec = list(sample_vec[i] + target_vec[i] for i in range(vec_len))
        diff_count = str(sum_vec).count('1')
        value_sum = vec_len - diff_count
        index_map[i+offset] = value_sum
    return index_map

def calculate_distance_multiprocess(target_vec):
    print('Start counting the neighbors...')
    global g_index_map
    target_vec = [int(x) for x in target_vec]
    cpu_core_num = multiprocessing.cpu_count()
    print('Current core count:' + str(cpu_core_num))
    unit_len = len(data_list)/cpu_core_num
    pool = Pool(cpu_core_num)
    for i in range(cpu_core_num):
        startpos = i*unit_len
        endpos = min((i+1)*unit_len, len(data_list))
        pool.apply_async(func=calculate_part, args=(target_vec, data_list[startpos:endpos], startpos), callback=callback_appenddict)
    pool.close()
    pool.join()
    index_sum_map = g_index_map
    return index_sum_map




def choose_neighbors(index_sum_map, data_list, target_vec):
    selected_data_list = []
    selected_index_list = []
    d_order=sorted(index_sum_map.items(),key=lambda x:x[1],reverse=True)
    mal_cnt = 0
    good_cnt = 0
    max_score = 0
    min_score = 10000

    start = 0
    end = NEIGHBOR_NUM
    for ii in d_order[start:end]:
        line = data_list[ii[0]]
        selected_index_list.append(ii[0])
        selected_data_list.append(line)
        ilabel = data_list[ii[0]][-1]
        max_score = max(max_score, ii[1])
        min_score = min(min_score, ii[1])
        if int(ilabel) == int('0'):
            good_cnt = good_cnt+1
        else:
            mal_cnt = mal_cnt+1
    return selected_data_list, selected_index_list


def choose_clf(selected_data_list, selected_index_list):
    clf_scores = predict_neighbor(selected_data_list, selected_index_list)
    calculate_f1(clf_scores)
    clf_order = sorted(clf_scores.items(),key=lambda x:x[1]['f1'],reverse=True)
    print('The prediction of the first-level model is completed, and the corresponding score of the model is:')
    for clf in clf_order:
        print(clf[0] + ': ' + str(clf[1]['f1']))

    clf_choose_score = []

    first_level_clf = clf_order[:FIRST_LEVEL_COUNT]
    clf_tag = []
    clf_list = []
    for clf_score in clf_order:
        precision = int(100 * clf_score[1]['f1'])
        if precision >= 94:
            print(clf_score[0] + 'f1 score:' + str(precision) + '%')
            clf_tag.append(clf_score[0])
            clf_list.append(clf_map[clf_score[0]])
            clf_choose_score.append(clf_score[1]['f1'])


    if len(clf_list)==0:
        clf_tag.append(clf_order[0][0])
        clf_tag.append(clf_order[1][0])
        clf_list.append(clf_map[clf_order[0][0]])
        clf_list.append(clf_map[clf_order[1][0]])
        clf_choose_score.append(clf_order[0][1]['f1'])
        clf_choose_score.append(clf_order[1][1]['f1'])
    print('The selected first-level model is as follows:' + str(clf_tag))

    return clf_tag, clf_choose_score
    
def get_stacking_file(target_vec, clf_tag, selected_data_list,clf_choose_score):

    target_vec = get_normalized_vector(target_vec)
    second_train_data = []
    for sample in selected_data_list:
        vector = get_normalized_vector(sample)
        second_train_data.append(vector)
    return clf_tag, second_train_data, target_vec,clf_choose_score



def predict_neighbor(selected_data_list, selected_index_list):

    clf_scores = {}
    for tag in tag_list:
        clf_scores[tag] = {}
        clf_scores[tag]['TN'] = 0.0
        clf_scores[tag]['FP'] = 0.0
        clf_scores[tag]['FN'] = 0.0
        clf_scores[tag]['TP'] = 0.0
        clf_scores[tag]['f1'] = 0.0
    
    print('Start predicting the neighbors')
    index = 0
    for sample in selected_data_list:
        vector = get_normalized_vector(sample)
        feature_vector = vector[:-1]
        label = vector[-1]
        feature_vector = np.array(feature_vector).reshape(1, -1)
        line_index = selected_index_list[index]
        predict_and_score(clf_scores, label, line_index)
        index = index + 1
    return clf_scores


def predict_and_score(clf_scores, label, line_index):
    for tag in tag_list:
        result = neighbor_result[line_index][tag]
        
        if int(result) == int(label):
            if int(label)==0:
                clf_scores[tag]['TN'] = clf_scores[tag]['TN']+1
            else:
                clf_scores[tag]['TP'] = clf_scores[tag]['TP']+1
        else:
            if int(label)==0:
                clf_scores[tag]['FP'] = clf_scores[tag]['FP']+1
            else:
                clf_scores[tag]['FN'] = clf_scores[tag]['FN']+1

def calculate_f1(clf_scores):
    for tag in tag_list:
        clf_score = clf_scores[tag]
        try:
            precision = clf_score['TP'] / (clf_score['TP']+clf_score['FP'])            
            recall = clf_score['TP'] / (clf_score['TP']+clf_score['FN'])
            clf_score['f1'] = 2 * (precision * recall) / ((precision + recall))
        except Exception,e:
            # ALL TN
            precision = clf_score['TN'] / (clf_score['TN']+clf_score['FN'])            
            recall = clf_score['TN'] / (clf_score['TN']+clf_score['FP'])
            clf_score['f1'] = 2 * (precision * recall) / ((precision + recall))


        
def get_normalized_vector(sample):
    sample = [int(x) for x in sample]
    return sample

def interface(dataList, clfmaps, neighborResult, file_path=None, target_vec=None):
    pass
    global clf_map, neighbor_result, data_list, tag_list
    tag_list = []
    for key in clfmaps.keys():
        tag_list.append(key)
    clf_map = clfmaps
    neighbor_result = neighborResult
    data_list = dataList
    print(len(clf_map))
    return process(file_path=file_path, target_vec=target_vec)    

    
if __name__ == '__main__':
    load_models()
    pass
    
    if len(sys.argv) <= 3:
        file_path = sys.argv[1]
        if len(sys.argv)>2:
            stacking_filepath =  sys.argv[2]
        print('stacking_filepath:' + stacking_filepath)
        mk_stackingfile_dir()
        print('--main--\n' + file_path)
        process(file_path=file_path)        
    elif len(sys.argv) == 4:
        stacking_filepath =  sys.argv[2]
        print('stacking_filepath:' + stacking_filepath)
        mk_stackingfile_dir()
        vector_list_path = stacking_filepath + 'feature.vec'
        target_vec = pickle.load(open(vector_list_path, 'rb'))
        process(target_vec=target_vec)    




                                                                                                                                                                                                                                                                                                     
        

