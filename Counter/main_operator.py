#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: Operator.py
@time: 2021/12/12 16:23
@desc:
'''
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

class Main_Operator(object):
    def __init__(self,counter,spincore):
        self.data_num_sign=0    #去除读出的第一个数值
        self.counter=counter    #计数卡对象
        self.spincore=spincore
        self.thread_stop=1      #读数时控制循环停止的标记
        self.spin_control_exist=0
        self.pool=ThreadPoolExecutor(max_workers=5)
        self.origin_data=np.zeros(10)
        self.data=np.zeros(10)
        self.counter_data=[]    #共聚焦扫描数据
        self.gui_state=1  #0:暂停  1：启动且是共聚焦模式   2：spincontrol模式
        self.counter_data_last = 0

        self.counter_record = []
        self.record_sign = 0


    def read_data(self,function_sign,list_length):
        self.counter_data_last=0
        while self.thread_stop:
            if function_sign==1:     #共聚焦扫描模式
                try:
                    # print('read_data')
                    # print(self.counter_data)
                    origin_data=self.counter.DAQ_Counter.read(list_length)
                    if len(self.counter_data) > 100:
                        self.counter_data.append(origin_data[0] - self.counter_data_last)  # 计数卡读数并处理
                        self.counter_data = self.counter_data[-100:]
                    else:
                        self.counter_data.append(origin_data[0] - self.counter_data_last)

                    self.counter_data_last = origin_data[0]
                    if self.record_sign:
                        self.counter_record.append(self.counter_data[-1])
                except:
                    print('read data failed(scan)')
                    pass


    def read_data_SpotsFind(self):
        origin_data = self.counter.DAQ_Counter.read(1)[0]
        data = origin_data - self.counter_data_last
        self.counter_data_last = origin_data
        return data


    def read_data_spincontrol(self,list_length,continue_sign):

        if continue_sign == 0:
            self.counter.DAQ_Counter.start()
            self.spincore.start_board_2()
            self.origin_data[1:] = self.counter.DAQ_Counter.read(list_length,20)
            self.counter.DAQ_Counter.stop()
            self.spincore.stop_board()
            self.data=np.diff(self.origin_data)

        if continue_sign == 1:
            self.origin_data[1:] = self.counter.DAQ_Counter.read(list_length,20)
            self.data=np.diff(self.origin_data)
            self.origin_data[0] = self.origin_data[-1]

        return self.data

    def reset_origin_data(self,list_length):
        self.origin_data=np.zeros(list_length+1,dtype=np.uint32)
        self.data=np.zeros(list_length,dtype=np.uint32)



#     def test(self,i):
#         print(i)
#         time.sleep(0.5)
#
# a=Main_Operator(1)
# a.pool.submit(a.test,2)
# time.sleep(0.5)
# a.pool.submit(a.test,3)