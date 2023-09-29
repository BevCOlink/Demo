# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2019-09-13 16:40:52
# @Last Modified by:   Yanff
# @Last Modified time: 2019-09-20 21:52:51
# from PyDAQmx import *
import Config,unit
import time,os
import OperationCode as OptC
import numpy as np
from ctypes import *
import constant as spinconst
import spinapi as spinpy
from Lockin_setup import MW_generater,lockin



filetime=time.strftime("%Y-%m-%d",time.localtime())
path = str('d:/data_autosave/'+filetime)
isExists=os.path.exists(path)
if not isExists:
    os.makedirs(path)



wordPumping=Config.SpinCoreGenWord({
    "AOM730":True,
    "CounterGate":True
    })
wordOperating=Config.SpinCoreGenWord({
    "MW"        :True,   
    "CounterGate":True
    })
wordOperating2=Config.SpinCoreGenWord({
    "MW"        :True, 
    "MW2"        :True,   
    "CounterGate":True
    })
wordIdle=Config.SpinCoreGenWord({
    "AOM730"     :False,
    "MW"        :False,
    "CounterGate":True
    }) 
wordODMR = Config.SpinCoreGenWord({
    "AOM730"     :True,
    "MW"        :True,
    "CounterGate":True
    }) 

Pumping =   [wordPumping,OptC.CONTINUE,0,3*unit.us]
Operating=  [wordOperating,OptC.CONTINUE,0,1*unit.us]
Operating_pluspi= [wordOperating,OptC.CONTINUE,0,1*unit.us]
Detecting=  [wordPumping,OptC.CONTINUE,0,3*unit.us]
Idle = [wordIdle,OptC.CONTINUE,0,1*unit.us]
Idle2 = [wordIdle,OptC.CONTINUE,0,0.2*unit.us]
pumpingODMR = [wordODMR,OptC.CONTINUE,0,10*unit.us]
Fill = [wordIdle,OptC.CONTINUE,0,0.2*unit.us]
Fill_minuspi= [wordIdle,OptC.CONTINUE,0,0.2*unit.us]

wordPumping_off=Config.SpinCoreGenWord({
    "AOM730":True,
    "CounterGate":False
    })
wordOperating_off=Config.SpinCoreGenWord({
    "MW"        :False,   
    "CounterGate":False
    })
wordOperating2_off=Config.SpinCoreGenWord({
    "MW"        :False, 
    "MW2"        :False,   
    "CounterGate":False
    })
wordIdle_off=Config.SpinCoreGenWord({
    "AOM730"     :False,
    "MW"        :False,
    "CounterGate":False
    }) 
wordODMR_off = Config.SpinCoreGenWord({
    "AOM730"     :True,
    "MW"        :False,
    "CounterGate":False
    }) 

Pumping_off =   [wordPumping_off,OptC.CONTINUE,0,3*unit.us]
Operating_off=  [wordOperating_off,OptC.CONTINUE,0,1*unit.us]
Detecting_off=  [wordPumping_off,OptC.CONTINUE,0,3*unit.us]
Idle_off = [wordIdle_off,OptC.CONTINUE,0,1*unit.us]
Idle2_off = [wordIdle_off,OptC.CONTINUE,0,0.2*unit.us]
pumpingODMR_off = [wordODMR_off,OptC.CONTINUE,0,10*unit.us]
Fill_off = [wordIdle_off,OptC.CONTINUE,0,0.2*unit.us]


# wordPumping_on=Config.SpinCoreGenWord({
#     "AOM730":True
#     "CounterGate"=True
#     })
# wordOperating_on=Config.SpinCoreGenWord({
#     "MW"        :True 
#     "CounterGate"=True   
#     })
# wordOperating2_on=Config.SpinCoreGenWord({
#     "MW"        :True, 
#     "MW2"        :True
#     "CounterGate"=True   
#     })
# wordIdle_on=Config.SpinCoreGenWord({
#     "AOM730"     :False,
#     "MW"        :False
#     "CounterGate"=True
#     }) 
# wordODMR_on = Config.SpinCoreGenWord({
#     "AOM730"     :True,
#     "MW"        :True
#     "CounterGate"=True
#     }) 

# Pumping =   [wordPumping_on,OptC.CONTINUE,0,3*unit.us]
# Operating=  [wordOperating_on,OptC.CONTINUE,0,1*unit.us]
# Detecting=  [wordPumping_on,OptC.CONTINUE,0,3*unit.us]
# Idle = [wordIdle_on,OptC.CONTINUE,0,1*unit.us]
# Idle2 = [wordIdle_on,OptC.CONTINUE,0,0.2*unit.us]
# pumpingODMR = [wordODMR_on,OptC.CONTINUE,0,10*unit.us]
# Fill = [wordIdle_on,OptC.CONTINUE,0,0.2*unit.us]


class Spin_control:

    def __init__(self,sample_rate,sample_size,lockin):
        self.spinpy = spinpy
        try:
            self.spinpy.pb_init()
        except:
            pass
        self.spinpy.pb_core_clock(500.0 *unit.MHz)
        # print(sample_rate)
        self.data_all = None
        self.data_single = None

        self.lockin = lockin
        self.lockin.lockin_ddef()

        self.x_data = None

        # self.integra_time = None
        self.sample_rate = sample_rate   
        self.sample_size = sample_size
        # self.sensit = sen[sensi]
        self.MW_gen = MW_generater()
        # print(self.MW_gen )
        # self.MW_gen
        
        self.cyc = -1
        self.state = False
        # self.task = Task()
        # self.task.CreateAIVoltageChan("Dev1/ai0","",DAQmx_Val_Diff,-10.0,10.0,DAQmx_Val_Volts,None)
        # self.task.CfgSampClkTiming("",sample_rate,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,sample_size)


    def start_ODMR(self,start_fre,end_fre,step_fre,MW_power,inte_time,loop_num):
        self.integra_time = inte_time
        # print(MW_power)
        self.MW_gen.MW_Power(MW_power)

        N = int((end_fre - start_fre)//step_fre)
        tempa = np.array(range(N+1))
        self.x_data = start_fre + step_fre*tempa
        
        InstListArray=[[]]
        InstListArray[0].append((wordODMR,OptC.LOOP,loop_num,0.01*unit.us))
        InstListArray[0].append(tuple(pumpingODMR))
        InstListArray[0].append(tuple(pumpingODMR))
        InstListArray[0].append((wordODMR,OptC.END_LOOP,0,0.01*unit.us))
        
        InstListArray[0].append((wordODMR_off,OptC.LOOP,loop_num,0.01*unit.us))
        InstListArray[0].append(tuple(pumpingODMR_off))
        InstListArray[0].append(tuple(pumpingODMR_off))
        InstListArray[0].append((wordODMR_off,OptC.END_LOOP,4,0.01*unit.us))
        
        InstListArray[0].append((wordODMR,OptC.BRANCH,0,0.01*unit.us))

        self.setSpincore(InstListArray[0])

        self.state = True
        self.data_single = np.zeros((N+1,), dtype=np.float64)
        self.data_all = np.zeros((N+1,), dtype=np.float64)
        num = 0
        print('read')
        while self.state:
            self.MW_gen.MW_Fre(self.x_data[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                
                self.data_all[:] = self.data_all[:] +self.data_single[:] 
                self.data_single = np.zeros((N+1,), dtype=np.float64) 
                
                self.cyc += 1
                dire = str(path + '/ODMR_' + filetime + '_%ddBm_%d.dat' %(MW_power,self.cyc))
                self.auto_save(dire,self.x_data,self.data_all)

            # time.sleep(inte_time)
            # print(inte_time)
            data = self.read_data(inte_time)
            self.data_single[num] = data

            print(num,data)


            num += 1
            num = num % (N+1)

        if self.state==False:
            self.close_task()
            # print('sssss')

    def start_pulse_ODMR(self,start_fre,end_fre,step_fre,MW_power,inte_time,MW_pi,pump_time,loop_num):
        self.integra_time = inte_time
        # print(MW_power)
        self.MW_gen.MW_Power(MW_power)

        N = int((end_fre - start_fre)//step_fre)
        tempa = np.array(range(N+1))
        self.x_data = start_fre + step_fre*tempa
        Pumping [3]  = pump_time*unit.us
        Operating[3]=MW_pi*unit.us

        InstListArray=[[]]
        InstListArray[0].append((wordPumping,OptC.LOOP,loop_num,pump_time*unit.us))
        InstListArray[0].append(tuple(Pumping))
        InstListArray[0].append(tuple(Idle))
        InstListArray[0].append(tuple(Operating))
        InstListArray[0].append(tuple(Fill))
        InstListArray[0].append((wordPumping,OptC.END_LOOP,0,pump_time*unit.us))
        
        InstListArray[0].append((wordPumping_off,OptC.LOOP,loop_num,pump_time*unit.us))
        InstListArray[0].append(tuple(Pumping_off))
        InstListArray[0].append(tuple(Idle_off))
        InstListArray[0].append(tuple(Operating_off))
        InstListArray[0].append(tuple(Fill_off))
        InstListArray[0].append((wordPumping_off,OptC.END_LOOP,6,pump_time*unit.us))
        
        InstListArray[0].append((wordPumping,OptC.BRANCH,0,pump_time*unit.us))

        self.setSpincore(InstListArray[0])

        self.state = True
        self.data_single = np.zeros((N+1,), dtype=np.float64)
        self.data_all = np.zeros((N+1,), dtype=np.float64)
        num = 0
        print('read')
        while self.state:
            self.MW_gen.MW_Fre(self.x_data[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                
                self.data_all[:] = self.data_all[:] +self.data_single[:] 
                self.data_single = np.zeros((N+1,), dtype=np.float64) 
                
                self.cyc += 1
                dire = str(path + '/pulse_ODMR_' + filetime + '_%ddBm_%s_%d.dat' %(MW_power,str(MW_pi),self.cyc))
                self.auto_save(dire,self.x_data,self.data_all)

            # time.sleep(inte_time)
            # print(inte_time)
            data = self.read_data(inte_time)
            self.data_single[num] = data

            print(num,data)


            num += 1
            num = num % (N+1)

        if self.state==False:
            self.close_task()
            # print('sssss')

    def start_Rabi(self,pump_time,detect_time,start_time,stop_time,pointN,MW_power,MW_fre,inte_time,loop_num):
        # self.integra_time = inte_time
        self.MW_gen.MW_Power(MW_power)
        self.MW_gen.MW_Fre(MW_fre)
        self.x_data = np.linspace(start_time,stop_time,pointN+1)
        Pumping [3]  = pump_time*unit.us
        Detecting [3] = detect_time*unit.us
        
        Pumping_off [3]  = pump_time*unit.us
        Detecting_off [3] = detect_time*unit.us
        
        InstListArray = []
        for j in range(pointN+1):
            InstListArray.append([])
            t=self.x_data[j]
            # print(t)
            Operating[3]=round(t*unit.us)  # Ramesy Time Change
            Operating_off[3]=round(t*unit.us)
            # print(t*unit.us)
            #InstListArray.append(Cooling)
            Fill[3]=(stop_time + 0.2-t)*unit.us
            Fill_off[3]=(stop_time + 0.2-t)*unit.us
            
            InstListArray[j].append((wordIdle,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operating))# pi/2
            InstListArray[j].append(tuple(Fill))
            # InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append((wordIdle,OptC.END_LOOP,0,0.01*unit.us))
            # InstListArray[j].append(tuple(Fill))
            
            InstListArray[j].append((wordIdle_off,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping_off))
            InstListArray[j].append(tuple(Idle_off))
            InstListArray[j].append(tuple(Operating_off))# pi/2
            InstListArray[j].append(tuple(Fill_off))
            # InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting_off))
            InstListArray[j].append((wordIdle_off,OptC.END_LOOP,7,0.01*unit.us))
            
            InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us)) #制造pump下调沿,实现计数采集,并开始下一序列循环
            
        self.state = True
        # self.data_single = np.zeros((self.sample_size,), dtype=np.float64)
        self.data_all = np.zeros((pointN+1,), dtype=np.float64)
        self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
        num = 0
        while self.state:
            self.setSpincore(InstListArray[num])
            # print(InstListArray[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                          
                
                self.data_all[:] = self.data_all[:] +self.data_single[:]
                self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
                self.cyc += 1
                dire = str(path + '/Rabi_' + filetime + '_%dMHz_%d.dat' %(MW_fre,self.cyc))
                # print(dire)
                
                self.auto_save(dire,self.x_data,self.data_all)

            
            # print(inte_time)
            # time.sleep(inte_time)
            data = self.read_data(inte_time)
            print(num,self.x_data[num],data)
            self.data_single[num] = data
            # print(self.state)
            num += 1
            num = num % (pointN+1)

        if self.state==False:
            self.close_task()

    def start_Ramsey(self,pump_time,detect_time,start_time,stop_time,pointN,MW_power,MW_fre,inte_time,MW_pi,loop_num):
        # self.integra_time = inte_time
        self.MW_gen.MW_Power(MW_power)
        self.MW_gen.MW_Fre(MW_fre)
        self.x_data = np.linspace(start_time,stop_time,pointN+1)

        Pumping [3]  = pump_time*unit.us
        Detecting [3] = detect_time*unit.us
        Operating[3]=MW_pi*unit.us 

        Pumping_off[3]  = pump_time*unit.us
        Detecting_off[3] = detect_time*unit.us
        Operating_off[3] =MW_pi*unit.us 

        delay = [wordIdle,OptC.CONTINUE,0,1*unit.us]
        delay_off = [wordIdle_off,OptC.CONTINUE,0,1*unit.us]

        InstListArray = []
        for j in range(pointN+1):
            InstListArray.append([])
            t=self.x_data[j]
            # print(t)
            delay[3]=round(t*unit.us)  # Ramesy Time Change
            # print(t*unit.us)
            #InstListArray.append(Cooling)
            delay_off[3]=round(t*unit.us)
            Fill[3]=(stop_time + 0.2-t)*unit.us
            Fill_off[3]=(stop_time + 0.2-t)*unit.us
            
            InstListArray[j].append((wordIdle,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operating))# pi/2
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Operating))# pi/2
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append(tuple(Fill))
            InstListArray[j].append((wordIdle,OptC.END_LOOP,0,0.01*unit.us))
            
            InstListArray[j].append((wordIdle_off,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping_off))
            InstListArray[j].append(tuple(Idle_off))
            InstListArray[j].append(tuple(Operating_off))# pi/2
            InstListArray[j].append(tuple(delay_off))
            InstListArray[j].append(tuple(Operating_off))# pi/2
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting_off))
            InstListArray[j].append(tuple(Fill_off))
            InstListArray[j].append((wordIdle_off,OptC.END_LOOP,9,0.01*unit.us))

            InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us))






        self.state = True
        # self.data_single = np.zeros((self.sample_size,), dtype=np.float64)
        self.data_all = np.zeros((pointN+1,), dtype=np.float64)
        self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
        num = 0
        while self.state:
            self.setSpincore(InstListArray[num])
            # print(InstListArray[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                          
                
                self.data_all[:] = self.data_all[:] +self.data_single[:]
                self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
                self.cyc += 1
                dire = str(path + '/Ramsey_' + filetime + '_%dMHz_%d.dat' %(MW_fre,self.cyc))
                # print(dire)
                
                self.auto_save(dire,self.x_data,self.data_all)

            
            # print(inte_time)
            # time.sleep(inte_time)
            data = self.read_data(inte_time)
            print(num,self.x_data[num],data)
            self.data_single[num] = data
            # print(self.state)
            num += 1
            num = num % (pointN+1)

        if self.state==False:
            self.close_task()

    def start_Hahn(self,pump_time,detect_time,start_time,stop_time,pointN,MW_power,MW_fre,inte_time,MW_pi_2,MW_pi,loop_num):
        # self.integra_time = inte_time
        self.MW_gen.MW_Power(MW_power)
        self.MW_gen.MW_Fre(MW_fre)
        self.x_data = np.linspace(start_time,stop_time,pointN+1)

        Operatingpi_2=  [wordOperating,OptC.CONTINUE,0,1*unit.us]
        Operatingpi=  [wordOperating,OptC.CONTINUE,0,2*unit.us]
        Operatingpi1=  [wordOperating,OptC.CONTINUE,0,2*unit.us]

        Operatingpi_2_off=  [wordOperating_off,OptC.CONTINUE,0,1*unit.us]
        Operatingpi_off=  [wordOperating_off,OptC.CONTINUE,0,2*unit.us]
        Operatingpi1_off=  [wordOperating_off,OptC.CONTINUE,0,2*unit.us]

        delay = [wordIdle,OptC.CONTINUE,0,1*unit.us]
        delay_off = [wordIdle_off,OptC.CONTINUE,0,1*unit.us]


        Pumping [3]  = pump_time*unit.us
        Detecting [3] = detect_time*unit.us

        Pumping_off [3]  = pump_time*unit.us
        Detecting_off [3] = detect_time*unit.us

        Operatingpi_2[3] = MW_pi_2*unit.us
        Operatingpi[3] = MW_pi*unit.us
        Operatingpi1[3] = MW_pi*unit.us

        Operatingpi_2_off[3] = MW_pi_2*unit.us
        Operatingpi_off[3] = MW_pi*unit.us
        Operatingpi1_off[3]= MW_pi*unit.us



        InstListArray = []
        for j in range(pointN+1):
            InstListArray.append([])
            t=self.x_data[j]
            # print(t)
            delay[3]=round(t*unit.us)  # Ramesy Time Change
            delay_off[3]=round(t*unit.us)
            # print(delay[3])
            Fill[3]=(2.0*stop_time + 0.5-2.0*t)*unit.us
            Fill_off[3]=(2.0*stop_time + 0.5-2.0*t)*unit.us
            


            InstListArray[j].append((wordIdle,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operatingpi_2))# pi/2
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Operatingpi))# pi
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Operatingpi_2))# pi/2
            InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append(tuple(Fill))
            InstListArray[j].append((wordIdle,OptC.END_LOOP,0,0.01*unit.us))
            # InstListArray[j].append(tuple(Fill))

            InstListArray[j].append((wordIdle_off,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping_off))
            InstListArray[j].append(tuple(Idle_off))
            InstListArray[j].append(tuple(Operatingpi_2_off))# pi/2
            InstListArray[j].append(tuple(delay_off))
            InstListArray[j].append(tuple(Operatingpi_off))# pi
            InstListArray[j].append(tuple(delay_off))
            InstListArray[j].append(tuple(Operatingpi_2_off))# pi/2
            InstListArray[j].append(tuple(Idle2_off))
            InstListArray[j].append(tuple(Detecting_off))
            InstListArray[j].append(tuple(Fill_off))
            InstListArray[j].append((wordIdle_off,OptC.END_LOOP,12,0.01*unit.us))

            InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us)) #制造pump下调沿,实现计数采集,并开始下一序列循环
            
        self.state = True
        # self.data_single = np.zeros((self.sample_size,), dtype=np.float64)
        self.data_all = np.zeros((pointN+1,), dtype=np.float64)
        self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
        num = 0
        self.x_data = self.x_data[:]*2
        while self.state:
            self.setSpincore(InstListArray[num])
            # print(InstListArray[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                          
                
                self.data_all[:] = self.data_all[:] +self.data_single[:]
                self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
                self.cyc += 1
                dire = str(path + '/Hahn_' + filetime + '_%dMHz_%d.dat' %(MW_fre,self.cyc))
                # print(dire)
                
                self.auto_save(dire,self.x_data,self.data_all)

            
            # print(inte_time)
            # time.sleep(inte_time)
            data = self.read_data(inte_time)
            print(num,self.x_data[num],data)
            self.data_single[num] = data
            # print(self.state)
            num += 1
            num = num % (pointN+1)

        if self.state==False:
            self.close_task()

    def start_T1(self,pump_time,detect_time,start_time,stop_time,pointN,MW_power,MW_fre,inte_time,MW_pi,loop_num):
        # self.integra_time = inte_time
        self.MW_gen.MW_Power(MW_power)
        self.MW_gen.MW_Fre(MW_fre)
        self.x_data = np.linspace(start_time,stop_time,pointN+1)

        Pumping [3]  = pump_time*unit.us
        Detecting [3] = detect_time*unit.us
        Operating[3]=MW_pi*unit.us 

        Pumping_off [3]  = pump_time*unit.us
        Detecting_off [3] = detect_time*unit.us
        Operating_off[3]=MW_pi*unit.us 

        delay = [wordIdle,OptC.CONTINUE,0,1*unit.us]
        delay_off = [wordIdle_off,OptC.CONTINUE,0,1*unit.us]

        InstListArray = []
        for j in range(pointN+1):
            InstListArray.append([])
            t=self.x_data[j]
            # print(t)
            delay[3]=t*unit.us  # Ramesy Time Change
            delay_off[3]=t*unit.us
            # print(t*unit.us)
            #InstListArray.append(Cooling)
            Fill[3]=(stop_time + 0.2-t)*unit.us
            Fill_off[3]=(stop_time + 0.2-t)*unit.us

            
            InstListArray[j].append((wordIdle,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operating))# pi
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append(tuple(Fill))
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append((wordIdle,OptC.END_LOOP,0,0.01*unit.us))


            InstListArray[j].append((wordIdle_off,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping_off))
            InstListArray[j].append(tuple(Idle_off))
            InstListArray[j].append(tuple(Operating_off))# pi
            InstListArray[j].append(tuple(delay_off))
            InstListArray[j].append(tuple(Detecting_off))
            InstListArray[j].append(tuple(Fill_off))
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Pumping_off))
            InstListArray[j].append((wordIdle_off,OptC.END_LOOP,9,0.01*unit.us))


            InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us)) #制造pump下调沿,实现计数采集,并开始下一序列循环
            
        self.state = True
        # self.data_single = np.zeros((self.sample_size,), dtype=np.float64)
        self.data_all = np.zeros((pointN+1,), dtype=np.float64)
        self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
        num = 0
        self.x_data = self.x_data[:] + Idle[3]/1000
        while self.state:
            self.setSpincore(InstListArray[num])
            # print(InstListArray[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                          
                
                self.data_all[:] = self.data_all[:] +self.data_single[:]
                self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
                self.cyc += 1
                dire = str(path + '/T1_' + filetime + '_%dMHz_%d.dat' %(MW_fre,self.cyc))
                # print(dire)
                
                self.auto_save(dire,self.x_data,self.data_all)

            
            # print(inte_time)
            # time.sleep(inte_time)
            data = self.read_data(inte_time)
            print(num,self.x_data[num],data)
            self.data_single[num] = data
            # print(self.state)
            num += 1
            num = num % (pointN+1)

        if self.state==False:
            self.close_task()

    def start_Ramsey_pluspi(self,pump_time,detect_time,start_time,stop_time,pointN,MW_power,MW_fre,inte_time,MW_pi,loop_num):

        # self.integra_time = inte_time
        self.MW_gen.MW_Power(MW_power)
        self.MW_gen.MW_Fre(MW_fre)
        self.x_data = np.linspace(start_time,stop_time,pointN+1)

        Pumping [3]  = pump_time*unit.us
        Detecting [3] = detect_time*unit.us
        Operating[3]=MW_pi*unit.us 

        Pumping_off[3]  = pump_time*unit.us
        Detecting_off[3] = detect_time*unit.us
        # Operating_off[3] =MW_pi*unit.us 
        Operating_pluspi[3] = MW_pi*3*unit.us

        delay = [wordIdle,OptC.CONTINUE,0,1*unit.us]
        delay_off = [wordIdle_off,OptC.CONTINUE,0,1*unit.us]

        Fill[3]= Fill_minuspi[3]+MW_pi*2*unit.us

        InstListArray = []
        for j in range(pointN+1):
            InstListArray.append([])
            t=self.x_data[j]
            # print(t)
            delay[3]=round(t*unit.us)  # Ramesy Time Change
            # print(t*unit.us)
            #InstListArray.append(Cooling)
            delay_off[3]=round(t*unit.us)
            Fill[3]=(stop_time + 0.2-t)*unit.us
            Fill_off[3]=(stop_time + 0.2-t)*unit.us
            
            InstListArray[j].append((wordIdle,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operating))# pi/2
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Operating))# pi/2
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append(tuple(Fill))
            InstListArray[j].append((wordIdle,OptC.END_LOOP,0,0.01*unit.us))
            
            InstListArray[j].append((wordIdle_off,OptC.LOOP,loop_num,0.01*unit.us))
            InstListArray[j].append(tuple(Pumping))
            InstListArray[j].append(tuple(Idle))
            InstListArray[j].append(tuple(Operating))# pi/2
            InstListArray[j].append(tuple(delay))
            InstListArray[j].append(tuple(Operating_pluspi))# 3pi/2
            #InstListArray[0].append(tuple(Fill))
            #InstListArray[j].append(tuple(Idle2))
            InstListArray[j].append(tuple(Detecting))
            InstListArray[j].append(tuple(Fill_minuspi))
            InstListArray[j].append((wordIdle_off,OptC.END_LOOP,9,0.01*unit.us))

            InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us))






        self.state = True
        # self.data_single = np.zeros((self.sample_size,), dtype=np.float64)
        self.data_all = np.zeros((pointN+1,), dtype=np.float64)
        self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
        num = 0
        while self.state:
            self.setSpincore(InstListArray[num])
            # print(InstListArray[num])
            if num == 0:
                filetime=time.strftime("%H-%M-%S",time.localtime())
                          
                
                self.data_all[:] = self.data_all[:] +self.data_single[:]
                self.data_single = np.zeros((pointN+1,), dtype=np.float64) 
                self.cyc += 1
                dire = str(path + '/Ramsey_' + filetime + '_%dMHz_%d.dat' %(MW_fre,self.cyc))
                # print(dire)
                
                self.auto_save(dire,self.x_data,self.data_all)

            
            # print(inte_time)
            # time.sleep(inte_time)
            data = self.read_data(inte_time)
            print(num,self.x_data[num],data)
            self.data_single[num] = data
            # print(self.state)
            num += 1
            num = num % (pointN+1)

        if self.state==False:
            self.close_task()


    def auto_save(self,dire,x_data,y_data):
        with open(dire,'w') as f1:
            f1.write('x(ns or MHz),y(V) \n')
            for i,j in zip(x_data,y_data):
                f1.write('%f, %f \n' % (i,j))
        f1.close()

    def read_data(self,timeout = 10.0):
        self.lockin.lockin_rest()
        
        self.lockin.lockin_samplerate(self.sample_rate)
        self.lockin.lockin_start()
        time.sleep(timeout)
        data = self.lockin.lockin_read(self.sample_size)

        # read = int32()
        # data = np.zeros((self.sample_size,), dtype=np.float64)
        # # time.sleep(0.05)
        # # self.task.ClearTask()
        # self.task.ReadAnalogF64(self.sample_size,timeout,DAQmx_Val_GroupByChannel,data,self.sample_size,byref(read),None)
        data_ave = sum(data)/self.sample_size
        return data_ave


    def setSpincore(self,InstList):
        self.spinpy.pb_stop()
        self.spinpy.pb_start_programming(spinconst.PULSE_PROGRAM)
        for Inst in InstList:
            # print(Inst)
            self.spinpy.pb_inst_pbonly(*Inst)
        self.spinpy.pb_stop_programming()
        self.spinpy.pb_start()
    def close_task(self):
        # self.task.ClearTask()
        self.spinpy.pb_stop()
        self.MW_gen.MW_off()
        # self.spinpy.pb_close()

    def __del__(self):
        print('dell')
        self.close_task()
        self.spinpy.pb_close()
        self.MW_gen.MW_off()
        # self.spinpy.pb_stop()



    
