import nidaqmx
from nidaqmx.constants import TriggerType, Edge, Level, AcquisitionType

Device_str=b"Dev1/ctr2"
TriggerGate="PFI9"
class Counter(object):
    def __init__(self,counter_update_time=100,Device_str=Device_str,TriggerGate=TriggerGate):
        self.Device_str=Device_str
        self.TriggerGate=TriggerGate
        self.counter_update_time=counter_update_time         #单位 ms
        self.DAQ_Counter = nidaqmx.Task()
        self.DAQ_Counter.ci_channels.add_ci_count_edges_chan(Device_str)
        self.DAQ_Counter.timing.cfg_samp_clk_timing(active_edge=Edge.FALLING, rate=1000,
                                               sample_mode=AcquisitionType.CONTINUOUS, source=self.TriggerGate)
        self.DAQ_Counter.triggers.pause_trigger.trig_type = TriggerType.NONE
        self.DAQ_Counter.in_stream.input_buf_size = 10000000


    def spin_control_setting(self):
        self.DAQ_Counter.stop()
        self.DAQ_Counter.triggers.pause_trigger.trig_type = TriggerType.DIGITAL_LEVEL
        self.DAQ_Counter.triggers.pause_trigger.dig_lvl_src = TriggerGate
        self.DAQ_Counter.triggers.pause_trigger.dig_lvl_when = Level.LOW
        # self.DAQ_Counter.start()

    def scanning_setting(self):
        self.DAQ_Counter.stop()
        self.DAQ_Counter.triggers.pause_trigger.trig_type = TriggerType.NONE
        self.DAQ_Counter.start()

    def scan_lock_setting(self):
        self.DAQ_Counter.triggers.pause_trigger.trig_type = TriggerType.NONE


if __name__ == "__main__":
    counter_test=Counter(Device_str,TriggerGate,2)
    counter_test.spin_control_setting()
    while 1:
        # counter_test.spincore.start_board()
        print(1)
        x=counter_test.DAQ_Counter.read(2)
        # counter_test.spincore.stop_board()

        print(x)