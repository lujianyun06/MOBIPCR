# -*- coding: utf-8 -*-


from __future__ import division
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import VMAnalysis
from androguard.decompiler.decompiler import DecompilerDAD
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis import analysis
from androguard.core.bytecodes import dvm
from constants import SPECIAL_STRINGS, DB_REGEX, API_CALLS, PERMISSIONS,NGRAM_THRE, VULNERABILITY
import hashlib
import math
from collections import Counter
import cPickle as pickle
import test_vul

# Extract all features for a given application
def extract_features(file_path,ngram_num):
    result = {}
    try:
        a = APK(file_path)
        d = DalvikVMFormat(a.get_dex())
        dx = VMAnalysis(d)
        vm = dvm.DalvikVMFormat(a.get_dex())
        vmx = analysis.uVMAnalysis(vm)
        d.set_vmanalysis(dx)
        d.set_decompiler(DecompilerDAD(d, dx))
    except:
        return None
    result['sha256'] = hashlib.sha256(a.get_raw()).hexdigest()
    result['feature_vectors'] = {}

    opt_seq = []
    for m in d.get_methods():
        for i in m.get_instructions():
            #in order to save space ,we store opcode instead of the name of optcode
            #opt_seq.append(i.get_name())
            #i.OP equals to i.get_op_value(), it's a decimal. we need transform it to hexdigest using hex method
            #like 84 in decimal is 0x54 in hex, and we need to cut the common string '0x' off using slice method
            opt_seq.append(str(hex(i.get_op_value()))[2:].zfill(2))
    print '*'*30,'NGRAM:',ngram_num
    optngramlist = [tuple(opt_seq[i:i+ngram_num]) for i in xrange(len(opt_seq) - ngram_num+1)]
    optngram = Counter(optngramlist)
    optcodes = dict()
    tmpCodes = dict(optngram)
    for k,v in optngram.iteritems():
        if v>=NGRAM_THRE:
            optcodes[str(k)] = v
    result['feature_vectors']['opt_codes'] = optcodes
    
    #add by ljy
    result['permissions'] = a.get_permissions()
    result['feature_vectors']['permissions'] = []
    for permission in PERMISSIONS:
        status = 1 if permission in result['permissions'] else 0
        result['feature_vectors']['permissions'].append(status)

    
    result['feature_vectors']['api_calls'] = []
    for call in API_CALLS:
        status = 1 if dx.tainted_packages.search_methods(".", call, ".") else 0
        result['feature_vectors']['api_calls'].append(status)   


    result['feature_vectors']['vulnerability'] = []
    apk_vul = test_vul.get_vul(file_path)
    result['vulnerability'] = apk_vul
    for vul in VULNERABILITY:
        status = 1 if vul in apk_vul else 0
        result['feature_vectors']['vulnerability'].append(status)


    return result
    

def create_vector_single(apk):
    feature_vector = []
    
    #modified to remove optcodes start
    #feature_vector.extend(apk['feature_vectors']['opt_codes'])
    optFile = open('optCodes.p','rb')
    optCodes = pickle.load(optFile)
    optFile.close()
    opt_codes = []
    tmp_codes = []
    tmp_permission = []
    tmp_apis = []
    
    feature_vector.extend(apk['feature_vectors']['permissions'])
    
    feature_vector.extend(apk['feature_vectors']['api_calls'])

    feature_vector.extend(apk['feature_vectors']['vulnerability'])
    
    for i in xrange(len(optCodes)):
        value = 0
        if optCodes[i] in apk['feature_vectors']['opt_codes']:
            #value = apk['feature_vectors']['opt_codes'][optCodes[i]]
            value = 1
        tmp_codes.append(value)
    # normalization values
    #max_v = max(tmp_codes)
    #min_v = min(tmp_codes)
    #for i in tmp_codes:
    #    opt_codes.append(i/(max_v-min_v))
    #feature_vector.extend(opt_codes)
    feature_vector.extend(tmp_codes)
    #modified to remove optcodes end  
    #print(feature_vector)
    
    return feature_vector
