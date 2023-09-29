#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: AFG31252-test.py
@time: 2022/3/21 20:03
@desc:
'''
import pandas as pd
import numpy as np
from tektronix_func_gen import FuncGen,FuncGenChannel
import pyvisa

def PLE_AFG_init():
    visa_add_AFG31252 = 'USB0::0x0699::0x035E::c016439::0::INSTR'
    AFG_gen = FuncGen(visa_address=visa_add_AFG31252, override_compatibility='AFG1022')
    AFG_ch = FuncGenChannel(fgen=AFG_gen, channel=1, impedance='50ohm')
    waveform=[0,1]
    AFG_gen.set_custom_waveform(waveform, memory_num=0, verify=False)

    AFG_ch.set_frequency(1, 'KHz')
    AFG_ch.set_amplitude(2)
    AFG_ch.set_offset(0)  # rate=35
    AFG_ch.set_burst_mode(idle='END')
    AFG_ch.set_trigger(slope='POSitive', source='EXTernal')
    AFG_ch.set_burst_cyc(1)
    AFG_ch.set_output_state('ON')

def R_spincontrol_init():
    visa_add_AFG31252 = 'USB0::0x0699::0x035E::c016439::0::INSTR'
    AFG_gen = FuncGen(visa_address=visa_add_AFG31252, override_compatibility='AFG1022')
    AFG_ch = FuncGenChannel(fgen=AFG_gen, channel=1, impedance='50ohm')
    AFG_ch.set_function_shape('DC')
    offset = 80.58 / 35 - 2
    AFG_ch.set_offset(offset)

def PLE_AFG_init_v2():

    visa_add_AFG31252 = 'USB0::0x0699::0x035E::c016439::0::INSTR'
    high = 140 / 35 - 2
    low = 0 / 35 - 2
    rm = pyvisa.ResourceManager()
    AFG31252 = rm.open_resource(visa_add_AFG31252)
    waveform=np.arange(1,10,0.1)
    waveform2=np.arange(1,10,5)
    waveform=np.append(waveform,waveform2[::-1])
    waveform = normalise_to_waveform(waveform)
    print(waveform,len(waveform))
    AFG31252.write_binary_values(
            "DATA:DATA EMEMory,", waveform, datatype="H", is_big_endian=True)
    AFG31252.write("FREQuency:FIXed %fHz" %0.5)
    AFG31252.write("VOLTage: LEVel:HIGH %fV" % high)
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)
    AFG31252.write("SOURce1:BURSt:IDLE END")
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)

def PLE_AFG_init_v3(waveform):
    visa_add_AFG31252 = 'USB0::0x0699::0x035E::c016439::0::INSTR'
    AFG_gen = FuncGen(visa_address=visa_add_AFG31252, override_compatibility='AFG1022')
    AFG_ch = FuncGenChannel(fgen=AFG_gen, channel=2, impedance='50ohm')
    AFG_gen.set_custom_waveform(waveform, memory_num=2, verify=False)

    AFG_ch.set_frequency(0.03, 'KHz')
    AFG_ch.set_amplitude(2)
    AFG_ch.set_offset(0)  # rate=35
    AFG_ch.set_burst_mode(idle='START')
    AFG_ch.set_trigger(slope='POSitive', source='EXTernal')
    AFG_ch.set_burst_cyc(1)
    AFG_ch.set_output_state('ON')

def PLE_AFG_init_v3_pyvisa(waveform):

    visa_add_AFG31252 = 'USB0::0x0699::0x035E::c016439::0::INSTR'
    high = 2
    low = 0
    rm = pyvisa.ResourceManager()
    AFG31252 = rm.open_resource(visa_add_AFG31252)
    # waveform=np.arange(1,10,0.1)
    # waveform2=np.arange(1,10,5)
    # waveform=np.append(waveform,waveform2[::-1])
    # waveform = [0,1,1,0,1,0,1]
    waveform = normalise_to_waveform(waveform)
    print(waveform,len(waveform))
    AFG31252.write_binary_values(
            "DATA:DATA EMEMory,", waveform, datatype="H", is_big_endian=True)
    AFG31252.write("FREQuency:FIXed %fKHz" %10)
    AFG31252.write("VOLTage: LEVel:HIGH %fV" % high)
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)
    AFG31252.write("SOURce1:BURSt:IDLE END")
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)
    AFG31252.write("VOLTage:LEVel:LOW %fV" % low)
    AFG31252.write(f'OUTPut{2}:STATe ON')
    print(AFG31252.query('*OPC?'))




def normalise_to_waveform(waveform):
    waveform = waveform - np.min(waveform)
    normalisation_factor = np.max(waveform)
    waveform = waveform / normalisation_factor * 16383
    return waveform.astype(np.uint16)

def list_to_TTL_waveform(sc_list,t_list,dt):    #t_list[0]需是最小公倍数
    find = 'eom'
    t_total=0
    waveform = np.array([])
    for t in t_list:
        for i in sc_list:

            if find in i[0]:
                num = int(t / dt)
                waveform = np.append(waveform, np.zeros(num, dtype=np.uint8) + 1)
                t_total+=t
            else:
                num = int(i[1] / dt)
                waveform = np.append(waveform, np.zeros(num, dtype=np.uint8))
                t_total += i[1]
    num = int(0.01/dt)
    waveform = np.append(waveform, np.zeros(num, dtype=np.uint8))
    t_total += 0.01
    return waveform,t_total

list =  [
    ('AOM|CounterGate|EOM_Trigger',    1),
    ('Idle',                           1),
    ('eom|Idle',                     't'),
    ('Idle',                         0.2),
    ('AOM',                         0.55),
    ('AOM|CounterGate',             0.55),
    ('Idle',                        0.02),
    ]
t_list = np.arange(0.002,0.022,0.002)
x,y= list_to_TTL_waveform(list,t_list,dt=0.002)
waveform = [0,1]
# PLE_AFG_init_v3_pyvisa(x)
# print(x)
PLE_AFG_init_v3_pyvisa(x)