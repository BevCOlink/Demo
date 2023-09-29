#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: microwave_device.py
@time: 2021/12/14 15:48
@desc:
'''
import pyvisa,clr
import time



class MW_generater():
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.N5181B_Address = u'USBInstrument1'
        self.N5181B = self.rm.open_resource(self.N5181B_Address)


    def set_MW_Freq(self, freq):
        self.N5181B.write(':SOUR:FREQ %f MHz' % freq)

    def set_MW_Ampl(self,ampl):
        self.N5181B.write(':SOUR:POW %f dBm' % ampl)

    def set_MW_ON(self):
        self.N5181B.write(':OUTP ON')

    def set_MW_OFF(self):
        self.N5181B.write(':OUTP OFF')


if __name__=='__main__':
    MW= MW_generater()
    x= MW.N5181B.query(':SOUR:FREQ?')
    print(x)