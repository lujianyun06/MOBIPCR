
# -*- coding: utf-8 -*-
'''
'''
import os
GOOD_TYPE = 'goodware'
BAD_TYPE = 'malware'
feature_count_map = {'goodware':20000, 'malware':20000}
optsfile_name = 'statisticOpts.txt'
mid_store_file = 'opt_tioe_score.txt'

def process(filename, limit_size, collection_list, dict_opts):
    opts = open(filename, "r")
    index = 0
    for line in opts:
        if not line.startswith('('):
            continue
        opt_score = line.strip().split('#')
        opt = opt_score[0]
        score = float(opt_score[1])
        
        index = index + 1
        #print(score)
        if not dict_opts.has_key(opt):
            dict_opts[opt] = {}
            dict_opts[opt]['value_sum'] = 0.0
            dict_opts[opt]['count'] = 0.0
        dict_opts[opt]['value_sum'] = dict_opts[opt]['value_sum'] + score
        dict_opts[opt]['count'] = dict_opts[opt]['count'] + 1



    
def save_to_file(d_order):
    opt_file = open(optsfile_name, 'w+')
    for d in d_order:
        opt_file.write(d[0] + '#'+str(d[1]['value_sum']) + '\n')
    opt_file.close()
    
    


if __name__ == '__main__':
    filename = 'selected_opts.p'
    collection_list = []
    dict_opts = {}
    process(GOOD_TYPE+filename, feature_count_map[GOOD_TYPE], collection_list,dict_opts)
    process(BAD_TYPE+filename, feature_count_map[BAD_TYPE], collection_list,dict_opts)
    d_order = sorted(dict_opts.items(),key=lambda x:x[1]['value_sum'],reverse=True)
    save_to_file(d_order)
    
    
    
    
    
    

