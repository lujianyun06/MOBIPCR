# -*- coding: utf-8 -*-

import sys
import os

sys.path.append('./..')

import traceback
import des2 as des
import stacking_custom as stacking
from django.conf import settings
import time

def detect_app(file_name):
	pass
	dir(settings)
	clf_map = settings.CLF_MAP
	neighbor_result = settings.DATA[0]
	data_list = settings.DATA[1]
	file_path = file_name
	time_start = time.time()
	try:
		print('----------------------------------------------- detect app')
		#get stacking file
		time1 = time.time()
		clf_tag, second_train_data, target_vec,clf_choose_score = des.interface(data_list, clf_map, neighbor_result, file_path)
		time2 = time.time()
		#stacking
		result = stacking.stack(clf_map, clf_tag, second_train_data, target_vec,clf_choose_score)
		time3 = time.time()
	except Exception as e:
		traceback.print_exc()
	finally:
		pass
	time_end = time.time()
	if result==1:
		print('it\'s a malware')
	else:
		print('it\'s a goodware')
	return result
	#return 1

if __name__ == '__main__':
	pass
	result = detect_app('./static/app.apk')
	print result