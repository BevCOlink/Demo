#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: SpinCore.py
@time: 2021/7/16/0028 19:39
@desc:
'''
from list_show_operator import list_show
from spinapi import *

class spincore():
    def __init__(self):
        pb_set_debug(0)
        pb_select_board(0)
        if pb_init() != 0:
            print("Error initializing board: %s" % pb_get_error())
            input("Please press a key to continue.")
            exit(-1)
        pb_core_clock(500)
        self._set_pin()
        self._set_word()
        self.set_ODMR_list()
        self.set_Rabi_list()
        self.set_NRabi_list()
        self.set_Hahn_list()
        self.set_Ramsey_lsit()
        self.set_T1_list()
        self.set_nuRabi_list()
        self.set_ODNMR_list()

    def _set_pin(self):
        self.SpinCorePin = {}
        self.SpinCorePin["AOM"] = 1  # 引脚1
        self.SpinCorePin["MW"] = 2
        self.SpinCorePin["CounterGate"] = 3
        self.SpinCorePin["RF"] = 4
        self.SpinCorePin["Trigger"] = 5

    def _set_word(self):
        self.wordTrigger = self.SpinCoreGenWord({
            'Trigger': True
        })
        self.wordInital = self.SpinCoreGenWord({
            'AOM': True
        })
        self.wordOperating = self.SpinCoreGenWord({
            "MW": True,
        })
        self.wordOperatingRF = self.SpinCoreGenWord({
            "RF": True,
        })
        self.wordDetecting = self.SpinCoreGenWord({
            'CounterGate': True,
        })
        self.wordIdle = self.SpinCoreGenWord({
            'AOM': False
        })
        self.wordmeasuring = self.SpinCoreGenWord({
            'AOM': True,
            'MW': True,
            'CounterGate': True
        })
        self.wordPuming = self.SpinCoreGenWord({
            'AOM': True,
            'MW': True,
        })
        self.wordRefering = self.SpinCoreGenWord({
            'AOM': True,
            'CounterGate': True
        })

    def set_ODMR_list(self):

        self.Pumping = [self.wordInital,Inst.CONTINUE, 0, 0.02 * us]
        self.ODMRmeasuring = [self.wordmeasuring,Inst.CONTINUE, 0, 500 * us]
        self.ODMMRpumping = [self.wordPuming,Inst.CONTINUE, 0, 500 * us]
        self.ODMRrefering = [self.wordRefering,Inst.CONTINUE, 0, 500 * us]

    def set_ODNMR_list(self):
        self.ODNMRPumping = [self.wordInital,Inst.CONTINUE, 0, 0.02 * us]
        self.ODNMRIdle = [self.wordIdle, Inst.CONTINUE, 0, 1 * us]
        self.ODNMROperating_MW = [self.wordOperating, Inst.CONTINUE, 0, 0.2 * us]
        self.ODNMROperating_RF = [self.wordOperatingRF, Inst.CONTINUE, 0, 0.2 * us]
        self.ODNMRDetecting = [self.wordRefering,Inst.CONTINUE, 0, 0.55 * us]

    def set_Rabi_list(self):
        self.RabiDetectRef = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.RabiDelay = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.RabiOperating = [self.wordOperating,Inst.CONTINUE,0,1*us]
        self.RabiFill = [self.wordIdle,Inst.CONTINUE,0,200*ns]
        self.RabiPreDetecting = [self.wordInital,Inst.CONTINUE,0,550*ns]
        self.RabiDetecting = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.RabiInit = [self.wordInital,Inst.CONTINUE,0,20*ns]

    def set_NRabi_list(self):
        self.NRabiDetectRef = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.NRabiDelay = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.NRabiOperating_MW = [self.wordOperating,Inst.CONTINUE,0,1*us]
        self.NRabiOperating_RF = [self.wordOperatingRF, Inst.CONTINUE, 0, 1 * us]
        self.NRabiFill = [self.wordIdle,Inst.CONTINUE,0,200*ns]
        self.NRabiPreDetecting = [self.wordInital,Inst.CONTINUE,0,550*ns]
        self.NRabiDetecting = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.NRabiInit = [self.wordInital,Inst.CONTINUE,0,20*ns]

    def set_Hahn_list(self):
        self.HahnGap = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.HahnDelay1 = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.HahnDelay2 = [self.wordIdle,Inst.CONTINUE,0,0.2*us]
        self.HahnDelay3 = [self.wordIdle, Inst.CONTINUE, 0, 200 * ns]
        self.HahnPumping = [self.wordRefering,Inst.CONTINUE, 0, 3 * us]
        self.HahnOperating_pid2 = [self.wordOperating, Inst.CONTINUE, 0, 1 * us]
        self.HahnOperating_pi = [self.wordOperating, Inst.CONTINUE, 0, 1 * us]
        self.HahnPreDetecting = [self.wordInital,Inst.CONTINUE, 0, 550*ns]
        self.HahnDetecting = [self.wordRefering,Inst.CONTINUE, 0, 550*ns]

    def set_Ramsey_lsit(self):
        self.RamseyGap = [self.wordIdle, Inst.CONTINUE, 0, 1 * us]
        self.RamseyPumping = [self.wordRefering, Inst.CONTINUE, 0, 3 * us]
        self.RamseyDelay1 = [self.wordIdle, Inst.CONTINUE, 0, 1 * us]
        self.RamseyDelay2 = [self.wordIdle, Inst.CONTINUE, 0, 150 * ns]
        self.RamseyDelay3 = [self.wordIdle, Inst.CONTINUE, 0, 20 * ns]
        self.RamseyOperating_pid2 = [self.wordOperating, Inst.CONTINUE, 0, 1 * us]
        self.RamseyPreDetecting = [self.wordInital, Inst.CONTINUE, 0, 550 * ns] #330
        self.RamseyDetecting = [self.wordRefering, Inst.CONTINUE, 0, 550 * ns]

    def set_T1_list(self):
        self.T1Gap = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.T1Delay1 = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.T1Delay2 = [self.wordIdle,Inst.CONTINUE,0,0.15*us]
        self.T1Delay3 = [self.wordIdle, Inst.CONTINUE, 0, 20 * ns]
        self.T1DelayRef = [self.wordIdle, Inst.CONTINUE, 0, 20 * ns]
        self.T1Pumping = [self.wordRefering,Inst.CONTINUE, 0, 3 * us]
        self.T1Operating_pi = [self.wordOperating, Inst.CONTINUE, 0, 1 * us]
        self.T1PreDetecting = [self.wordInital,Inst.CONTINUE, 0, 550*ns]
        self.T1Detecting = [self.wordRefering,Inst.CONTINUE, 0, 550*ns]

    def set_nuRabi_list(self):
        self.nuRabiDetectRef = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.nuRabiDelay = [self.wordIdle,Inst.CONTINUE,0,1*us]
        self.nuRabiOperating = [self.wordTrigger,Inst.CONTINUE,0,1*us]
        self.nuRabiPreDetecting = [self.wordInital,Inst.CONTINUE,0,550*ns]
        self.nuRabiDetecting = [self.wordRefering,Inst.CONTINUE,0,550*ns]
        self.nuRabiInit = [self.wordInital,Inst.CONTINUE,0,20*ns]

    def programming_board(self,pluse_time):
        pb_set_debug(0)
        pb_select_board(0)
        pb_init()
        pb_core_clock(500)
        List = [[]]
        list1 = [0xF, Inst.CONTINUE, 0, pluse_time/2 * ms]
        List[0].append(tuple(list1))
        list2 = [0x1, Inst.BRANCH, 0, pluse_time/2 * ms]
        List[0].append(tuple(list2))

        pb_start_programming(PULSE_PROGRAM)
        for l in List[0]:
            pb_inst_pbonly(*l)

        pb_stop_programming()
    def porgramming_board_v2(self,list):
        pb_stop()
        pb_set_debug(0)
        pb_select_board(0)
        pb_init()
        pb_core_clock(500)
        pb_start_programming(PULSE_PROGRAM)
        for l in list[0]:
            pb_inst_pbonly(*l)

        pb_stop_programming()

    def str_list_to_list(self,str_list,t_list=[0.2]):
        InstListArray = [[]]
        word_list = []
        for i in str_list:
            pin_list = i[0].split('|')
            pin_dict = {}
            for pin in pin_list:
                if pin == 'Idle':
                    pin_dict['AOM'] = False
                else:
                    pin_dict[pin] = True
            try:
                word_list.append(self.SpinCoreGenWord(pin_dict))
            except SyntaxError as e:
                print('No %s pin, try to check pin definition\n' %i[0])
                print(e[0])
                return False

        i = 0
        for t in t_list:
            for key in str_list:
                if key[1] == 't':
                    InstListArray[0].append(tuple([word_list[i], Inst.CONTINUE, 0, round(t,2) * us]))
                else:
                    InstListArray[0].append(tuple([word_list[i], Inst.CONTINUE, 0, key[1] * us]))
                i+=1
            i=0
        InstListArray[0].append(tuple([self.wordIdle, Inst.BRANCH, 0, 10 * ns]))
        print(InstListArray)
        return InstListArray






    #########用来处理传入的字典，变换为二进制信号
    def SpinCoreGenWord(self,wordDict):
        word = 0
        for key in wordDict:
            if wordDict[key]:
                word += 1 << (self.SpinCorePin[key] - 1)
        return word

    def start_board(self):
        pb_reset()
        pb_start()
    def start_board_2(self):
        pb_start()

    def close_board(self):
        pb_stop()
        pb_close()

    def stop_board(self):
        pb_stop()





if __name__ == "__main__":
    sp=spincore()
    ls=list_show()
    list=[[]]
    list[0].append((0x08, Inst.CONTINUE, 0, 500 * ms))
    list[0].append((0x00, Inst.CONTINUE, 0, 500 * ms))
    list[0].append((0x08, Inst.CONTINUE, 0, 500 * ms))
    list[0].append((0x00, Inst.CONTINUE, 0, 500 * ms))
    list[0].append((0x08, Inst.CONTINUE, 0, 200 * ms))
    list[0].append((0x00, Inst.CONTINUE, 0, 200 * ms))
    list[0].append((0x08, Inst.CONTINUE, 0, 200 * ms))
    list[0].append((0x00, Inst.BRANCH, 0, 200 * ms))
    # ls.bit_list_show(list[0],4)
    print(list)


    sp.porgramming_board_v2(list)
    sp.start_board()
    print('finished')