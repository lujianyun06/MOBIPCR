#!/usr/env/bin python
#coding=utf-8

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig

from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report

def save_roc(clf_list,x_test,y_test,styles,labels,name):
    '''
        save roc curve to file.
        clf_list: classifier list
        x_test:
        y_test:
        styles: curve style: b--
        labels: represent which classifier it is in roc_curve
        name: file name being saved
    '''
    index = 0
    for clf in clf_list:
        print('roc: %s',labels[index])
        y_true = y_test
        y_pred = clf.predict(x_test) 
        y_pred_pro = clf.predict_proba(x_test) 
        y_scores = pd.DataFrame(y_pred_pro,columns=clf.classes_.tolist())[1].values

        print(classification_report(y_true,y_pred))
        auc_value = roc_auc_score(y_true,y_scores)
        fpr,tpr,thresholds = roc_curve(y_true,y_scores,pos_label=1.0)
        lw = 2
        #plt.plot(fpr,tpr,color=colors[index],linestyle=linestyles[index],linewidth=lw,label='[ %s ]Roc cuve(area = %0.4f)' %(label,auc_value))
        plt.plot(fpr,tpr,styles[index],linewidth=lw,label='[%s] Roc curve(area = %0.4f)' %(labels[index],auc_value))
        index += 1

        plt.plot([0,1],[0,1],color='navy',linewidth=lw,linestyle='--')
        plt.xlim([0.0,1.0])
        plt.ylim([0.0,1.0])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc='lower right')
    savefig(name)

