#!/usr/bin/env python
#coding = utf-8

'''
print and save log to file

'''
def log(content,name='result_mlp.print',mode='a'):
    print content
    f = open(name,mode)
    print >> f,content
    f.close()


