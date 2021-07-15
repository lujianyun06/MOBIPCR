#-*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import scipy as sp
import copy,os,sys,psutil
import lightgbm as lgb
from lightgbm.sklearn import LGBMRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import dump_svmlight_file

from sklearn import  metrics   #Additional scklearn functions
from sklearn.grid_search import GridSearchCV   #Perforing grid search


from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
from sklearn import datasets

print(__doc__)

def searchMP(X,Y,test_size):
    '''
    using GridSearch and Cross-Validation to find best model and parameters
    model: svm with kernel of RBF or linear
    parameters: C & gamma(no for linear kernel) & iter etc.
    '''
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size = test_size,random_state=0)
    #set the parameters by cross_validation
    scores = ['average_precision','roc_auc']
    param_test = {
            'max_depth':range(5,15,2),
            'num_leaves':range(10,40,5),
            }

    for score in scores:
        print("# Tuning hyper-parameters for %s" %score)
        print()
        
        estimator = LGBMRegressor(
           num_leaves = 50, # cv调节50是最优值
               max_depth = 13,
               learning_rate =0.1, 
               n_estimators = 1000, 
               objective = 'regression', 
               min_child_weight = 1, 
               subsample = 0.8,
               colsample_bytree=0.8,
               nthread = 7,
        )   
        clf = GridSearchCV(estimator,param_grid=param_test,scoring ='%s' %score ,cv=5)

        clf.fit(x_train,y_train)

        print("Best parameters set found on development set:")
        print()
        print(clf.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        for params,mean_score,scores in clf.grid_scores_:
            print("%0.3f (+/-%0.3f) for %r" % (mean_score,scores.std()*2,params))
        print()
        print('Best params:')
        best_parameters = clf.best_estimator_.get_params()
        for param_name in sorted(param_test.keys()):
            print("\t%s:%r" %(param_name,best_parameters[param_name]))


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

'''
Driver Function
Usage: python model_train.py train_test/k-fold [roc]
'''
if __name__ == "__main__":

	# Check for arguments
	if len(sys.argv) <= 1:
                print('memory percent:'+(str)(psutil.virtual_memory().percent)+'%')
		# Load the data
                print("load data")
		data = load_data()

		# Shuffle the data
		#random.shuffle(data)
                x = [x[:-1] for x in data[:]]
                y = [y[-1] for y in data[:]]
                #set train_test split propotion 
                test_size = 0.1

                # start to find best model and parameters
                searchMP(np.array(x),np.array(y),test_size)
	else:
		print('[+] Usage: python grid_search.py')
	 

