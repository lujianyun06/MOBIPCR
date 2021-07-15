#-*- coding:utf-8 -*-

class tag_constant:

    ADA_TAG = 'Ada'
    RF_TAG = 'RF'
    KNN_TAG = 'KNN'
    LGBM_TAG = 'LGBM'
    SVM_TAG = 'SVM'
    GBC_TAG = 'GBC'

    tag_list = [
        ADA_TAG, 
        RF_TAG, 
        LGBM_TAG, 
        GBC_TAG, 
        SVM_TAG,
        KNN_TAG
        ]


class score_util:
    @staticmethod
    def record_one_score(result, label,score):
        label = int(label)
        if int(result)==label:
            if label==1:
                score['TP'] = score['TP'] + 1
            else:
                score['TN'] = score['TN'] + 1
        else:
            if label==1:
                score['FN'] = score['FN'] + 1
            else:
                score['FP'] = score['FP'] + 1
    
                          
    @staticmethod    
    def get_score(score):
        print(score)
        precision = 0
        recall = 0
        f1 = 0
        try:
            precision1 = score['TP'] / (score['TP']+score['FP'])
            recall1 = score['TP'] / (score['TP']+score['FN'])
            precision2 = score['TN'] / (score['TN']+score['FN'])
            recall2 = score['TN'] / (score['TN']+score['FP'])

            precision = (precision1+precision2)/2
            recall = (recall1+recall2)/2
            f1 = 2 * (precision * recall) / ((precision + recall))
        except:            
            pass
        return precision, recall, f1
    
    @staticmethod
    def get_accuracy(score):
        accuracy = 0
        try:
            accuracy = (score['TP']+score['TN'])/(score['TP']+score['TN']+score['FP']+score['FN'])
        except:            
            pass           
        return accuracy

class test_data_loader:
    test_start = 0
    test_end = 20
    test_data_name = 'test_data.csv'

    @staticmethod
    def load_data_typediff(in_goodlimit, in_mallimit, in_startpos, in_endpos):
        print('load_data_typediff goodlimit=%d, mallimit=%d, startpos=%d, endpos=%d'%(in_goodlimit, in_mallimit, in_startpos, in_endpos))
        feature_vectors = []
        good_limit = in_goodlimit
        mal_limit = in_mallimit
        good_cnt = 0
        mal_cnt = 0
        start_pos = in_startpos
        end_pos = in_endpos
        with open(test_data_loader.test_data_name,'r') as fp:
            for i,line in enumerate(fp):
                ll = [int(x.strip()) for x in line.split('$')]
                label = ll[-1]
                if i < start_pos:
                    continue
                if i>= end_pos:
                    break
                if label == 1 and mal_cnt < mal_limit:
                    mal_cnt = mal_cnt + 1
                    feature_vectors.append(ll)
                elif label == 0 and good_cnt < good_limit:
                    good_cnt = good_cnt + 1
                    feature_vectors.append(ll)
                elif good_cnt >= good_limit and mal_cnt >= mal_limit:
                    break
        print('len of feature_vectors=%d'%(len(feature_vectors)))
        return feature_vectors
            
    @staticmethod
    def load_data_range():
        feature_vectors = []
        with open(test_data_loader.test_data_name,'r') as fp:
            for i,line in enumerate(fp):
                if i < test_start:
                    continue
                elif i >= test_end:
                    break
                feature_vectors.append([int(x.strip()) for x in line.split('$')])
        return feature_vectors
    
    @staticmethod
    def load_data(in_goodlimit, in_mallimit, in_startpos, in_endpos):
        #return test_data_loader.load_data_range()
        return test_data_loader.load_data_typediff(in_startpos=in_startpos, in_endpos=in_endpos, in_goodlimit=in_goodlimit, in_mallimit=in_mallimit)
    
    
    
           

