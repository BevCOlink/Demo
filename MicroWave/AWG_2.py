import zhinst.ziPython
import zhinst.utils
import common_shfsg
import time
import json
import os
import numpy as np

device_id = 'dev12151'
server_host = "localhost"
server_port = 8004
interface = "usb"
channel1 = 0
channel2 = 1


class MW_generater():
    def __init__(self):
        # connect device
        self.daq = zhinst.ziPython.ziDAQServer(host=server_host, port=server_port, api_level=6)
        self.daq.connectDevice(device_id, interface)
        print(zhinst.utils.api_server_version_check(self.daq))

    def set_MW_Freq(self, freq_mw, freq_rf):
        synth_nmbr1 = self.daq.getInt(f"/{device_id}/SGCHANNELS/{channel1}/SYNTHESIZER")
        synth_nmbr2 = self.daq.getInt(f"/{device_id}/SGCHANNELS/{channel2}/SYNTHESIZER")
        # Turn on output
        # self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Set SHFSG to use RF path (in case LF path was enabled earlier)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/RFLFPATH", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel2}/OUTPUT/RFLFPATH", 0)
        # Set center frequency, 微波需大于 600 MHz
        self.daq.setDouble(
            f"/{device_id}/SYNTHESIZERS/{synth_nmbr1}/CENTERFREQ", np.round(freq_mw * 1e-2) * 1e8
        )
        self.daq.setDouble(f"/dev12151/sgchannels/{channel2}/digitalmixer/centerfreq", 0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/OSCS/0/FREQ",
                           (freq_mw * 1e-2 - np.round(freq_mw * 1e-2)) * 1e8)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/OSCS/0/FREQ", freq_rf * 1e6)

        self.daq.sync()

    def set_MW_Ampl(self, power_mw, power_rf):
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/RANGE", power_mw)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/OUTPUT/RANGE", power_rf)
        # Turn on I port of sine generator
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/I/ENABLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/I/ENABLE", 1)
        # Turn on Q port of sine generator
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/Q/ENABLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/Q/ENABLE", 1)

        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/I/COS/AMPLITUDE", 0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/I/SIN/AMPLITUDE", -0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/Q/COS/AMPLITUDE", 0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/Q/SIN/AMPLITUDE", 0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/I/COS/AMPLITUDE", 0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/I/SIN/AMPLITUDE", -0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/Q/COS/AMPLITUDE", 0.7)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel2}/SINES/0/Q/SIN/AMPLITUDE", 0.7)

        self.daq.sync()

    def set_MW_ON(self):
        self.daq.sync()
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/ON", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel2}/OUTPUT/ON", 1)

    def set_MW_OFF(self):
        self.daq.sync()
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/ON", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel2}/OUTPUT/ON", 0)


if __name__ == '__main__':
    MW = MW_generater()
    MW.set_MW_Freq(1000, 20)
    MW.set_MW_Ampl(-20, -20)
    MW.set_MW_ON()
