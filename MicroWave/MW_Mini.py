#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: MW_Source.py
@time: 2021/12/28 11:32
@desc:
'''
import clr
clr.FindAssembly('mcl_gen64.dll')
from mcl_gen64 import *

class mini_MW_generater():
    def __init__(self):
        self.gen = usb_gen()
        self.gen.Connect()

    def set_MW_Freq(self,freq):
        SN=self.gen.SetFreq(freq,0)
        return SN
    def set_MW_Ampl(self,ampl):
        SN=self.gen.SetPower(ampl,0)
        return SN

    def set_MW_ON(self):
        self.gen.SetPowerON()

    def set_MW_OFF(self):
        self.gen.SetPowerOFF()

if __name__=='__main__':
    import time
    MW=mini_MW_generater()
    MW.set_MW_Ampl(-60)
    MW.set_MW_Freq(1310)
    MW.set_MW_ON()
    time.sleep(1)
    MW.set_MW_OFF()