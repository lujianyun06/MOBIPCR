#-*- coding:utf-8 -*-
import sys
import os
import subprocess
import time
import stacking_custom as stacking
import traceback
import shutil
import des2 as des
from util4predict import tag_constant
import cPickle as pickle

clf_map = {}

neighbor_result = []

data_list = []

def load_models():
    global clf_map
    tag_list = tag_constant.tag_list
    modelPath = './final_models/'
    for tag in tag_list:
        if tag=='KNN':
            continue
        clf = pickle.load( open( modelPath + "train_data_" + tag + ".p", "rb" ))
        print(tag + ' load completed')
        clf_map[tag] = clf
    print( len(clf_map))

def load_neighbor_result():
    global neighbor_result
    neighbor_result = pickle.load( open('./2rd_neighbor_result.p', "rb" ))
    print('neighbor_result' + ' load completed')


def load_data_list():
    global data_list
    data_list = pickle.load( open('./2rd_data_list.p', "rb" ))
    print('data_list' + ' load completed')

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        print('!!!This file must be run as Python 2!!!')
        d = sys.argv[1]
        unique_flag = str(int(round(time.time() * 1000)))
        
        index = 0
        mal = 0
        good = 0
        start_time = time.time()
        load_models()
        load_neighbor_result()
        load_data_list()
        for root, dirs, files in os.walk(d):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    index = index + 1
                    print('----------------------------------------------- app' + file_path + " "+str(index))
                    param = "\"" + file_path + "\""
                    #get stacking file
                    time1 = time.time()
                    clf_tag, second_train_data, target_vec,clf_choose_score = des.interface(data_list, clf_map, neighbor_result, file_path)
                    time2 = time.time()
                    #stacking
                    result = stacking.stack(clf_map, clf_tag, second_train_data, target_vec,clf_choose_score)
                    time3 = time.time()
                    if result == 1:
                        mal = mal+1
                    else:
                        good = good +1
                    print('good=' + str(good) + "  mal=" + str(mal))
                except Exception as e:
                    traceback.print_exc()
                finally:
                    #shutil.rmtree(stacking_path)
                    pass
        print('good=' + str(good))
        print('mal=' + str(mal))
        end_time = time.time()
    else:
        print('Do you forget add an apk path?')
