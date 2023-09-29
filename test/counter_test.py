# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2020-12-04 19:29:49
# @Last Modified by:   Yanff
# @Last Modified time: 2020-12-04 19:36:23
import nidaqmx
import time
from nidaqmx.constants import TriggerType, Edge, Level, AcquisitionType
counter=b"Dev1/ctr2"
Samples = 1000
TimeOut = 1
TriggerGate="PFI9"
DAQ_counter = nidaqmx.Task()
DAQ_counter.ci_channels.add_ci_count_edges_chan(counter)      #counter=b"Dev2/ctr2",
DAQ_counter.timing.cfg_samp_clk_timing(active_edge=Edge.RISING, rate=5000,
                                               sample_mode=AcquisitionType.CONTINUOUS,source=TriggerGate)
# DAQ_counter.triggers.pause_trigger.trig_type = (TriggerType.DIGITAL_LEVEL)
# DAQ_counter.triggers.pause_trigger.dig_lvl_src = TriggerGate
# DAQ_counter.triggers.pause_trigger.dig_lvl_when = Level.LOW
DAQ_counter.start()
dd = 0
data1=[]
while True:

	# TempData = DAQ_counter.read(number_of_samples_per_channel=8)
	# data=TempData[0]-dd
	# print(data)
	# dd = TempData[0]
	print(DAQ_counter.read(number_of_samples_per_channel=10))
