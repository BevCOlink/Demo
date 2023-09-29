#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: AFG3052C.py
@time: 2022/8/1 19:28
@desc:
'''
import pyvisa
import numpy as np

def normalise_to_waveform(waveform):
    waveform = waveform - np.min(waveform)
    normalisation_factor = np.max(waveform)
    waveform = waveform / normalisation_factor * 16383
    return waveform.astype(np.uint16)

def list_to_TTL_waveform(sc_list, t_list=[0.2], dt=0.001,max=1):  # t_list[0]需是最小公倍数
    find = 'eom'
    t_total = 0
    waveform = np.array([])
    for t in t_list:
        for j,i in enumerate(sc_list):
            if find in i[0]:
                if i[1] == 't':
                    num = int(t / dt)
                    t_total += t
                else:
                    num = int(i[1] / dt)
                    t_total += i[1]
                waveform = np.append(waveform, np.zeros(num)+max)
            else:
                if i[1] == 't':
                    num = int(t / dt)
                    t_total += t
                else:
                    num = int(i[1] / dt)
                    t_total += i[1]
                waveform = np.append(waveform, np.zeros(num))

            try:
                if i[2] == 'END_LOOP':
                    loop = sc_list[i[3]]
                    for _ in np.arange(0,loop[3]-1,1):
                        for ii in sc_list[i[3]:j+1]:
                            if find in ii[0]:
                                if ii[1] == 't':
                                    num = int(t / dt)
                                    t_total += t
                                else:
                                    num = int(ii[1] / dt)
                                    t_total += ii[1]
                                waveform = np.append(waveform, np.zeros(num)+ max)
                            else:
                                if ii[1] == 't':
                                    num = int(t / dt)
                                    t_total += t
                                else:
                                    num = int(ii[1] / dt)
                                    t_total += ii[1]
                                waveform = np.append(waveform, np.zeros(num))
            except:
                pass

    num = int(0.01 / dt)
    waveform = np.append(waveform, np.zeros(num))
    return waveform, round(t_total,2)

visa_add_AFG3052C = 'USB0::0x0699::0x0352::C010446::0::INSTR'
rm = pyvisa.ResourceManager()
AFG3052C = rm.open_resource(visa_add_AFG3052C)
list=[
    ('AOM|CounterGate|AFG_Trigger', 1),
    ('AOM_Rlaser', 1),
    ('eom|AOM_Rlaser|CounterGate', 1000),
    ('Idle', 1),
    ('AOM_Rlaser|AFG_Trigger',          1),
    ('AOM_Rlaser',   0.04,  'LOOP',    100),
    ('AOM_Rlaser',       0.08,  'END_LOOP',  5),
    ('CounterGate',                       1),
    ]

list2=[
    ('AOM|CounterGate|AFG_Trigger', 1),
    ('AOM_Rlaser', 1),
    ('AOM_Rlaser|CounterGate', 1000),
    ('Idle', 1),
    ('AOM_Rlaser|AFG_Trigger',          1),
    ('eom|AOM_Rlaser',   0.04,  'LOOP',    100),
    ('AOM_Rlaser',       0.08,  'END_LOOP',  5),
    ('CounterGate',                       1),
    ]

waveform,period = list_to_TTL_waveform(sc_list=list,dt = 0.04)
waveform = normalise_to_waveform(waveform)
print(len(waveform))
AFG3052C.write_binary_values(
            "DATA:DATA EMEMory,", waveform, datatype="H", is_big_endian=True)
AFG3052C.write("DATA:COPY USER3,EMEMory")

waveform2,period2 = list_to_TTL_waveform(sc_list=list2,dt = 0.04)
waveform2 = normalise_to_waveform(waveform2)
AFG3052C.write_binary_values(
            "DATA:DATA EMEMory,", waveform2, datatype="H", is_big_endian=True)
AFG3052C.write("DATA:COPY USER4,EMEMory")


f = 1/period *1000
print(f)
high = 0.5
low = 0
AFG3052C.write("SOURce1:FREQuency:FIXed %fKHz" % f)
AFG3052C.write("VOLTage:HIGH %fV" % high)
AFG3052C.write("VOLTage:LOW %fV" % low)
AFG3052C.write("TRIGger:SLOPe POSitive")
AFG3052C.write("TRIGger:SOURce EXTernal")
AFG3052C.write("BURSt:MODE TRIGgered")
AFG3052C.write("BURSt:NCYCles 1")
AFG3052C.write("OUTPut1:STATe ON")

AFG3052C.write("SOURce2:FREQuency:FIXed %fKHz" % f)
AFG3052C.write("SOURce2:VOLTage:HIGH %fV" % high)
AFG3052C.write("SOURce2:VOLTage:LOW %fV" % low)
AFG3052C.write("SOURce2:TRIGger:SLOPe POSitive")
AFG3052C.write("SOURce2:TRIGger:SOURce EXTernal")
AFG3052C.write("SOURce2:BURSt:MODE TRIGgered")
AFG3052C.write("SOURce2:BURSt:NCYCles 1")
AFG3052C.write("SOURce2:OUTPut1:STATe ON")









