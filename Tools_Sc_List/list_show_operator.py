#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: list_show_operator.py
@time: 2022/1/2 15:54
@desc:
'''

import matplotlib.pyplot as plt
import numpy as np

class list_show():
    def __init__(self):
        self.y_bit_list=[]    #所有通道的电平集合，二维数组，第一维表示通道数，第二维表示list个数
        self.x_time_list=[0]  #记录时间的list，一维
        self.bit_num=[]       #一维，表示通道序号
        self._label=['914-AOM','MW','CounterGate','Trigger','914-Shutter','AFGTrigger','AOM_Rlaser']
        self._color=["b","g","r","c","m","y","k"]


    def bit_list_show(self,list,entrance_num):
        self.bit_num=np.arange(0,entrance_num,1)
        self.x_time_list = [0]
        self.y_bit_list=[]
        num=0
        for i in self.bit_num:
            self.y_bit_list.append([0+2*i])
        for i in list:
            for j in self.bit_num:
                self.y_bit_list[j].append(self.bit_separate(i[0],j)+2*j)
            self.x_time_list.append(i[3]+self.x_time_list[num])
            num+=1
        #单位：ms
        self.x_time_list=np.array(self.x_time_list)
        self.x_time_list=self.x_time_list/1e6

        for i in self.bit_num:
            plt.step(self.x_time_list,self.y_bit_list[i],color=self._color[i], where="pre", lw=2)

        plt.legend(labels=self._label[0:entrance_num],loc='lower right',fontsize=6)
        plt.xlim(0, self.x_time_list[-1])
        plt.show()


    def bit_separate(self,byte,index):
        if byte & (1<<index):
            return 1
        else:
            return 0


if __name__ == "__main__":
    ls=list_show()
    ls.step_plot([0,0.05,0.5],[0,1,0])
