import zhinst.ziPython
import zhinst.utils
import common_shfsg
import time
import json
import os

device_id = 'dev12151'
server_host = "localhost"
server_port = 8004
interface = "usb"
channel = 0


class MW_generater():
    def __init__(self):
        # connect device
        self.daq = zhinst.ziPython.ziDAQServer(host=server_host, port=server_port, api_level=6)
        self.daq.connectDevice(device_id, interface)
        print(zhinst.utils.api_server_version_check(self.daq))

    def set_parameter(self, output_power, rf_frequency, rflf_path, osc_frequency):
        synth_nmbr = self.daq.getInt(f"/{device_id}/SGCHANNELS/{channel}/SYNTHESIZER")
        # Turn on output
        # self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Set SHFSG to use RF path (in case LF path was enabled earlier)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/RFLFPATH", rflf_path)
        # Set RF center frequency
        if rflf_path == 1:
            self.daq.setDouble(
                f"/{device_id}/SYNTHESIZERS/{synth_nmbr}/CENTERFREQ", rf_frequency * 1e6
            )
        else:
            self.daq.setDouble(f"/{device_id}/sgchannels/{channel}/digitalmixer/centerfreq", rf_frequency * 1e6)
        # Set power in dBm, in steps of 5dBm
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/RANGE", output_power)

        ## Configure digital modulation
        # Set modulation frequency
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/OSCS/0/FREQ", osc_frequency * 1e6)
        # Set sine generator
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/OSCSELECT", 0)
        # Set harmonic of sine generator
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/HARMONIC", 1)
        # Set phase of sine generator
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/PHASESHIFT", 0)
        # Gains
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/0/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/0/gains/1", -1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/1/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/1/gains/1", 1.0)
        # Global Amplitude
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/OUTPUTAMPLITUDE", 0.5)
        # Enable digital modulation
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/MODULATION/ENABLE", 1)

        # Set marker source
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/MARKER/SOURCE", 0)

    def set_MW_ON(self):    # trigger 测试
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.sync()
        awg_seqc = """
                const s_rate = 2.0e9;
                const t = 1.0e-6;
                const s_t = round(s_rate*t/16)*16;
                wave w = ones(s_t);
                assignWaveIndex(1,2,w,1,2,w,0);
                while (true){
                  waitDigTrigger(1);
                  resetOscPhase();
                  setTrigger(1);
                  setTrigger(0);
                  executeTableEntry(1);
                  playZero(s_t);
                }
            """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)

        # Upload command table to instrument
        ct = [
            {
                "index": 0,
                "waveform": {
                    "index": 0
                },
                "amplitude00": {
                    "value": 0.0,
                },
                "amplitude01": {
                    "value": -0.0,
                },
                "amplitude10": {
                    "value": 0.0,
                },
                "amplitude11": {
                    "value": 0.0,
                }
            },
            {
                "index": 1,
                "waveform": {
                    "index": 0
                },
                "amplitude00": {
                    "value": 0.5,
                },
                "amplitude01": {
                    "value": -0.5,
                },
                "amplitude10": {
                    "value": 0.5,
                },
                "amplitude11": {
                    "value": 0.5,
                }
            }
        ]
        ct_str = {
            "$schema": "https://docs.zhinst.com/shfsg/commandtable/v1_0/schema#",
            "header": {
                "version": "1.0"
            },
            "table": ct}
        self.daq.setVector(f"/{device_id}/SGCHANNELS/{channel}/AWG/COMMANDTABLE/DATA", json.dumps(ct_str))
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Enable sequencer with single mode
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 1)

        print(
            f"Rabi sequence with frequency generated on channel {channel}."
        )

    def set_MW_OFF(self):
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 0)


if __name__ == '__main__':
    MW = MW_generater()

