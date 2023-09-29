#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: test.py
@time: 2022/6/27 23:20
@desc:
'''
import time,threading
import operator
Y1=1
Y2=2
x= 0
#
a='Y3=Y1+Y2'
exec(a)
print(Y3)

# def func(i):
#     global x
#     x=1
#     global Y1
#     Y1=2*i
#     time.sleep(1)
#     print(Y1)
#     x=0
#
# for i in [1,2]:
#     if x == 1:
#         thd.join()
#     thd = threading.Thread(target=func,args=[i])
#
#     thd.start()
#     print('aaa')
#     time.sleep(0.6)
