#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
import os
import json
# import detect_bridge
import detect_bridge2 as detect_bridge

import random
import time
from django.conf import settings
import shutil
import traceback



# Create your views here.
def index(request):
	pass
	return HttpResponse(u"welcome")


def mk_work_dir(path):
    print('asd')
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        pass
        traceback.print_exc()


def recv_apk(req):
    if req.method == 'POST':
        time_stamp = req.POST.get('time_stamp')
        recv_file = req.FILES.get('apk')
        print("***********")
        #
        # filepath = os.path.join(settings.MEDIA_ROOT,filename)
        # f = open(filepath,'wb+')
        # for i in myfile.chunks():
        #     f.write(i)
        # f.close()
        parent_path = './static/'
        print(parent_path)
        tmp = str(time_stamp) + str(int(round(time.time() * 1000)))
        try:
            parent_path = parent_path + tmp + '/'
            mk_work_dir(parent_path)


            filename = 'app.apk'
            filepath =  parent_path+ filename
            fullpath = os.path.join(os.getcwd(), filepath)
            print(fullpath)

            file = open(fullpath, 'wb+')
            for chunk in recv_file.chunks(chunk_size=1024):
        	   file.write(chunk)
            file.close()

        except Exception as e:
            traceback.print_exc()

        print('app store completed')
        resp = {}
        
        try:
            result = detect_bridge.detect_app(fullpath)
            resp['app_flag'] = result
            resp['code'] = '200'
        except Exception as e:
            print(e)
            resp['app_flag'] = 0
            resp['code'] = '500'
        finally:
            os.remove(fullpath)
            shutil.rmtree(parent_path)

        return HttpResponse(json.dumps(resp))


