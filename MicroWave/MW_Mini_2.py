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

SN1 = '11804010011'
SN2 = '12007060011'

class mini_MW_generater():
    def __init__(self):
        self.gen1 = usb_gen()
        self.gen1.Connect(SN1)
        self.gen2 = usb_gen()
        self.gen2.Connect(SN2)

    def set_MW_Freq(self, freq_MW, freq_RF, control):
        SN_1 = self.gen1.SetFreq(freq_MW, 0)
        if control == 1:
            SN_2 = self.gen2.SetFreq(freq_RF, 0)
        else:
            SN_2 = 0
        return SN_1, SN_2

    def set_MW_Ampl(self, ampl_MW, ampl_RF, control):
        SN_1 = self.gen1.SetPower(ampl_MW, 0)
        if control == 1:
            SN_2 = self.gen2.SetPower(ampl_RF, 0)
        else:
            SN_2 = 0
        return SN_1, SN_2

    def set_MW_ON(self, control):
        self.gen1.SetPowerON()
        if control == 1:
            self.gen2.SetPowerON()
        else:
            pass

    def set_MW_OFF(self, control):
        self.gen1.SetPowerOFF()
        if control == 1:
            self.gen2.SetPowerOFF()
        else:
            pass


if __name__ == '__main__':
    import time
    MW = mini_MW_generater()
    MW.set_MW_Ampl(-60, -60, 1)
    MW.set_MW_Freq(1310, 9, 1)
    MW.set_MW_ON(1)
    time.sleep(1)
    MW.set_MW_OFF(1)
