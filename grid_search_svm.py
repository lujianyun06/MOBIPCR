'''
Author: Bingfei Ren
Description: This code trains the malware detection model

'''
from __future__ import print_function
import sys
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
import time

print(__doc__)

def searchMP(X,Y,test_size):
    '''
    using GridSearch and Cross-Validation to find best model and parameters
    model: svm with kernel of RBF or linear
    parameters: C & gamma(no for linear kernel) & iter etc.
    '''
    x_train,x_test,y_train,y_test = train_test_split(X,Y,test_size = test_size,random_state=0)
    #set the parameters by cross_validation
    tuned_parameters = [{'kernel':['rbf'],'gamma':map(lambda x : 2**x,[-5,-4,-3,-2,-1,0,1,2]),'C':map(lambda x : 2**x,[-3,-2,-1,0,1,2,3,4,5,6,7])},
            {'kernel':['linear'],'C':map(lambda x : 2**x,[-3,-2,-1,0,1,2,3,4,5,6,7])}]
    
    #tuned_parameters = [{'kernel':('linear','rbf'),'C':map(lambda x : 2**x,[-3,-2,-1,0,1,2,3,4,5,6,7])}]
    
    scores = ['precision','recall']

    for score in scores:
        print("# Tuning hyper-parameters for %s" %score)
        print()

        #clf = GridSearchCV(svm.SVC(C=1),tuned_parameters,cv=5,scoring='%s_weighted' %score)
        clf = GridSearchCV(svm.SVC(),tuned_parameters)
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
        print("Detailed classification report:")
        print()
        print('The model is trained on the full development set.')
        print('The scores are computed on the full evaluation set.')
        print()
        y_true,y_pred = y_test,clf.predict(x_test)
        print(classification_report(y_true,y_pred))
        print()


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
				feature_vector.append([int(x.strip()) for x in line.split(',')])
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

		# Shuffle the data
		#random.shuffle(data)
                x = [x[:-1] for x in data[:]]
                y = [y[-1] for y in data[:]]
                #set train_test split propotion 
                test_size = 0.3

                # start to find best model and parameters
                startT = time.time()
                searchMP(x,y,test_size)
                print('cost time:%0.3f' %(time.time()-startT))
	else:
		print('[+] Usage: python grid_search.py')
	 

