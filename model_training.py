#coding=utf-8

'''
Author: ljy
Description: This code trains the malware detection model

'''

import pickle, cPickle  #sPickle
import datetime
import sys
from sklearn import svm
import random
from sklearn.feature_selection import SelectFromModel
from sklearn.svm import LinearSVC
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.metrics import roc_curve,auc
import numpy as np
from scipy import interp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from lightgbm.sklearn import LGBMClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
import plot_roc
import plot_prc
import time
import rbf_print as rp
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier

def load_data():
    feature_vector = []
    # Data format
    # Column 0: Class label (1: Malware, 0: Benign)
    # OPEN TRAIN_DATA
    with open('train_data.csv','r') as fp:
        for i,line in enumerate(fp):
            feature_vector.append([int(x.strip()) for x in line.split('$')])
    return feature_vector


def load_test():
    feature_vector = []
    # Data format
    # Column 0: Class label (1: Malware, 0: Benign)
    # Column 1-19: Features
    # OPEN TEST_DATA
    with open('neighbor_data.csv','r') as fp:
        for i,line in enumerate(fp):
            feature_vector.append([int(x.strip()) for x in line.split('$')])
    return feature_vector


'''
Driver Function
Usage: python model_train.py train_test/k-fold [roc]
'''
if __name__ == "__main__":

    # Check for arguments
    if len(sys.argv) <= 1:
        # Load the data
        data = load_data()
        test = load_test()
        # Shuffle the data
        random.shuffle(data)
        random.shuffle(test)

        testLength = int(0.6*len(test))

        trainX = [x[:-1] for x in data]
        trainY = [y[-1] for y in data]

        testX = np.array([x[:-1] for x in test[testLength:]])
        testY = np.array([y[-1] for y in test[testLength:]])

        clf_svm = svm.SVC(kernel='linear',C=0.5,probability=True)

        
                #KNN
        clf_knn = KNeighborsClassifier(leaf_size=26,n_jobs=-1,n_neighbors=13)

                #AdaBoost   

        dtc = DecisionTreeClassifier(criterion='entropy',splitter='random')
        clf_adaboost = AdaBoostClassifier(base_estimator=dtc,n_estimators=7)

                #RandomForest

        clf_rf = RandomForestClassifier(random_state=14,max_depth=18,min_samples_leaf=2,criterion='gini')

                #LightGBM LGBMClassifier

        clf_lgbm = LGBMClassifier(
                        num_leaves = 35,
                        max_depth = 13,
                        learning_rate=0.1,
                        n_estimators=1000,
                        objective='regression',
                        min_child_weight=1,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        nthread=-1,
        )

        

                #save clf to plot roc_curve
                #clf_list = [clf_knn,clf_adaboost,clf_nb,clf_rf,clf_lgbm,clf_svm]
        #clf_list = [clf_adaboost,clf_rf,clf_lgbm,clf_knn]
                #clf_labels = ['knn','ada','nb','rf','lgbm','svm']
        #clf_labels = ['Ada','RF','LGBM', 'KNN']
        
        
        clf_gbc =  GradientBoostingClassifier(learning_rate=1.0, n_estimators=150, max_leaf_nodes=35, max_depth=6)
        clf_list = [clf_adaboost,clf_rf,clf_lgbm,clf_gbc,clf_svm,clf_knn,]
        clf_labels = ['Ada','RF','LGBM', 'GBC','SVM','KNN']
        
        # Perform training
        index = 0
        for clf in clf_list:
            rp.log('[{}] Training the data....'.format(clf_labels[index]))
            clf.fit(np.array(trainX), np.array(trainY))
            rp.log('[{}] default Accuracy: {:.3f}%'.format(clf_labels[index],clf.score(testX, testY)*100))
            predicted = clf.predict(testX)
            rp.log(metrics.classification_report(testY,predicted))
            rp.log(metrics.confusion_matrix(testY,predicted))
            # Save the trained model so that it can be used later
            cPickle.dump(clf, open( "./final_models/ap1/train_data_"+clf_labels[index]+".p", "wb" ))
            rp.log('Model trained and saved.')
            index += 1

        #plot roc_curve and save
        #styles = ['b-','g-','k-','r-','c-','y-']
        styles = ['b-','g-','r-','y-','k-']
               
        #png file name
        # strftime is different from linux to Windows.
        #in linux its: %Y-%m-%d-%H-%M-%s
        #while in windows its: %Y-%m-%d-%H-%M-%S
        name = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        plot_roc.save_roc(clf_list,testX,testY,styles,clf_labels,name)

    else:
        print '[+] Usage: python {}>'.format(__file__)
    

