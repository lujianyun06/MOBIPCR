#-*- coding:utf-8 -*-
from sklearn.model_selection import KFold
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin, clone
import numpy as np
import math
 
class StackingAveragedModels(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, base_models, meta_model, clf_choose_score,n_folds=5, fit_base=True):
        self.base_models = base_models
        self.meta_model =  meta_model
        self.n_folds = n_folds
        self.fit_base = fit_base
        self.clf_choose_score = clf_choose_score
        self.total_sum = 0
        for score in self.clf_choose_score:
            self.total_sum = self.total_sum + score
        # print self.clf_choose_score
        # print self.total_sum
        # print len(base_models)

 
    #clone orginal model to fit
    def fit(self, X, y):
        self.base_models_ = [list() for x in self.base_models]
        self.meta_model_ = clone(self.meta_model)
        kfold = KFold(n_splits=self.n_folds, shuffle=True, random_state=156)
 
        out_of_fold_predictions = np.zeros((X.shape[0], len(self.base_models)))
        for i, model in enumerate(self.base_models):
            for train_index, holdout_index in kfold.split(X, y):
                if self.fit_base == True:
                    instance = clone(model)
                    instance.fit(X[train_index], y[train_index])
                else:
                    pass
                    instance = model
                self.base_models_[i].append(instance)
                y_pred = instance.predict(X[holdout_index])
                out_of_fold_predictions[holdout_index, i] = y_pred
 
        # fit secondary model
        self.meta_model_.fit(out_of_fold_predictions, y)
        return self

    # more performance more weight
    def weight_predict(self, X, model, index):
        # print self.base_models
        sum_len = len(self.base_models)
        # print('index=' + str(index))
        # print(type(model))
        weight = self.clf_choose_score[index]/self.total_sum
        predict = model.predict(X) * weight
        base = sum_len-index-(sum_len/2)
        re = max(1,(sum_len-index+1)) ** (base) * predict
        return re

    #use base model and weight to predict
    def predict(self, X):
        meta_features = np.column_stack([
            np.column_stack([self.weight_predict(X,model,i) for i,model in enumerate(self.base_models)]).mean(axis=1)
            for base_models in self.base_models_])
        result = self.meta_model_.predict(meta_features)
        # meta_features = np.column_stack([
        #     np.column_stack([self.weight_predict(X,model,i) for model in base_models]).mean(axis=1)
        #     for i,base_models in enumerate(self.base_models_)])
        # result = self.meta_model_.predict(meta_features)
        result = abs(result)
        print result
        return result