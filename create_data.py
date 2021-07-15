# -*- coding: utf-8 -*-


from pymongo import MongoClient
from constants import DB_NAME,TNGRAM_THRE
from core2 import create_vector_single
from collections import *
import cPickle as pickle
'''

'''

client = MongoClient()
db = client[DB_NAME]

permissions = []
apis = []
vul = []

# Get unique permissions
with open('unique_permissions.txt','r') as fp1:
    for line in fp1:
        permissions.append(line.strip().replace(",","").replace("'",""))

# Get apis
with open('api.txt','r') as fp2:
    for line in fp2:
        apis.append(line.strip().replace(",","").replace("'",""))


# get vulnerability
with open('vulnerability.txt', 'r') as fpv:
    for line in fpv:
        vul.append(line.strip().replace(",","").replace("'",""))    

#modified to remove optcodes start
#Get optCodes
print 'start to generate selected features'

# Create opt_codes
optsfile_name = 'final_opts_file.txt'
optCodes = []
optstxt_file = open(optsfile_name, 'r')
for line in optstxt_file:
    opt = line.strip()
    optCodes.append(opt)

print 'end to generate selected feature'
print 'generate opt_codes end. start to dump optCodes'
optFile = open('optCodes.p','wb')
pickle.dump(optCodes,optFile,True)
optFile.close()

features = permissions + apis + vul + optCodes
#modified to remove optcodes end

'''
features.append('com.metasploit.stage.PayloadTrustManager')
features.append('entropy_rate')
features.append('native')
features.append('db')
features.append('class')
'''
features.append('type')

with open('data.csv','w+') as op:
    header = ""
    for f in features:
        header+= f.strip().replace('"','')+'$'
    header = header[:-1]
    op.write(header+'\n')

    index = 0
    for apk in db.apk.find():
        print 'index:',index
        index += 1
        feature_vector = create_vector_single(apk)
        str_to_write = ""
        for i,feature in enumerate(feature_vector):
            if i < len(feature_vector)-1:
                str_to_write+=str(feature)+'$'
            else:
                class_label = 1 if apk['data_type'] == 'malware' else 0
                str_to_write+=str(feature)+'$'+str(class_label)
        op.write(str_to_write+'\n')




