#!/usr/bin/python 
# -- coding: utf-8 --
import datetime
import sys
import random
import numpy as np
from scipy import interp
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig

import time
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
import cPickle as pickle
from CustomStackingModels import StackingAveragedModels
from util4predict import tag_constant


def load_data():
    feature_vector = []
    # Data format
    # Column 0: Class label (1: Malware, 0: Benign)
    # Column 1-19: Features
    with open('final_data.csv','r') as fp:
        for i,line in enumerate(fp):
            if i == 0:
                pass
            else:
                feature_vector.append([int(x.strip()) for x in line.split('$')])
    return feature_vector


def load_models():
    modelPath = './final_models/'
    tag_list = tag_constant.tag_list
    for tag in tag_list:
        clf = pickle.load( open( modelPath + "train_data_" + tag + ".p", "rb" ))
        print(tag + ' load completed')
        clf_map[tag] = clf
    


ADA_TAG = 'Ada'
RF_TAG = 'RF'
KNN_TAG = 'KNN'
LGBM_TAG = 'LGBM'
SVM_TAG = 'SVM'
GBC_TAG = 'GBC'

clf_map = {
    ADA_TAG: clf_adaboost,
    RF_TAG: clf_rf,
    KNN_TAG: clf_knn,
    LGBM_TAG: clf_lgbm,
    SVM_TAG: clf_svm,
    GBC_TAG: clf_gbc
}

def stack(fitted_clfs, clf_tag, second_train_data, target_vec,clf_choose_score):
    print('enter stacking')
    pass
 
    data = second_train_data
    feature_vector = np.array(target_vec).reshape(1, -1)
    #second training
    trainLength = int(1 * len(data))
    
    clf_map = fitted_clfs

    clf_list = []
    for tag in clf_tag:
        clf = clf_map[tag]
        clf_list.append(clf)

    # Training Data
    trainX = np.array([x[:-1] for x in data[:trainLength]])
    trainY = np.array([y[-1] for y in data[:trainLength]])

    # Testing Data = 0
    testX = np.array([x[:-1] for x in data[trainLength:]])
    testY = np.array([y[-1] for y in data[trainLength:]])

    lr = LogisticRegression(n_jobs=-1)

    sclf = StackingAveragedModels(clf_list, lr, clf_choose_score,n_folds=3, fit_base=False)

    
    feature_vector = np.array(feature_vector).reshape(1, -1)
    sclf.fit(trainX, trainY)
    result = sclf.predict(feature_vector)
    # print('res = '+str(result[0]))
    ans = result
    print('ans = '+str(ans))
    return ans

file_path='./stacking_file/'
if __name__ == "__main__":
    global clf_map
    load_models()
    fitted_clfs = clf_map
    clf_tag = pickle.load(open(file_path + 'clf_tag', 'rb'))
    second_train_data = pickle.load(open(file_path+'second_train_data', 'rb'))
    target_vec = pickle.load(open(file_path+'target_vec', 'rb'))
    stack(fitted_clfs, clf_tag, second_train_data, target_vec)
