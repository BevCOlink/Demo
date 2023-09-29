# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2020-12-04 19:29:49
# @Last Modified by:   Yanff
# @Last Modified time: 2020-12-04 19:36:23
import nidaqmx
import time
from nidaqmx.constants import TriggerType, Edge, Level, AcquisitionType
counter=b"Dev1/ctr1"
freq=1  #单位HZ
duty=0.1  #占空比
Samples = 1000
TimeOut = 1
if __name__ == "__main__":
    DAQ_counter = nidaqmx.Task()
    DAQ_counter.co_channels.add_co_pulse_chan_freq(counter,freq=freq,duty_cycle=duty)      #counter=b"Dev2/ctr2",
    DAQ_counter.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
    DAQ_counter.start()
    while 1:
        pass

