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
            self.daq.setDouble(f"/dev12151/sgchannels/{channel}/digitalmixer/centerfreq", rf_frequency * 1e6)
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
        self.daq.sync()

    def set_MW_ON(self):

        awg_seqc = """
                const s_rate = 2.0e9;
                const t = 1.0e-6;
                const s_t = round(s_rate*t/16)*16;
                wave w = ones(s_t);
                assignWaveIndex(1, 2, w, 1, 2, w, 0);
                while (true){
                  resetOscPhase();
                  setTrigger(1);
                  setTrigger(0);
                  playWave(1, 2, w, 1, 2, w);
                  playZero(s_t);
                }
            """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)

        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Configure single mode
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 1)

        print(
            "playWave"
        )

    def set_MW_ON2(self):

        awg_seqc = """
                        const s_rate = 2.0e9;
                        const t = 1.0e-6;
                        const s_t = round(s_rate*t/16)*16;                       
                        var i;
                        while (true){{
                          const s_len = round(s_rate*80*1.0e-9/16)*16;
                          const s_step = round(s_rate*80*1.0e-9/16)*16;
                          for (i=0;i<20;i++){{
                            wave w = ones(s_len);
                            // waitDigTrigger(1);
                            resetOscPhase();
                            setTrigger(1);
                            setTrigger(0);
                            playZero(s_t);
                            playWave(1,2,w,1,2,w);
                            waitWave();
                            s_len = s_len + s_step;
                          }}
                        }}
                    """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)

        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Configure single mode
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 1)

        print(
            "playWave2"
        )

    def set_MW_ON_table(self):

        awg_seqc = """
                const s_rate = 2.0e9;
                const t = 0.2e-6;
                const s_t = round(s_rate*t/16)*16;
                wave w = ones(s_t);
                assignWaveIndex(1,2,w,1,2,w,0);
                while (true){
                  resetOscPhase();
                  setTrigger(1);
                  executeTableEntry(1);
                  waitWave();
                  setTrigger(0);
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
                    # "increment": false
                },
                "amplitude01": {
                    "value": -0.0,
                    # "increment": false
                },
                "amplitude10": {
                    "value": 0.0,
                    # "increment": false
                },
                "amplitude11": {
                    "value": 0.0,
                    # "increment": false
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
            "table"
        )

    def set_MW_ON2_table(self):   # table, predefined

        awg_seqc = f"""
                        const s_rate = 2.0e9;
                        const t = 1.0e-6;
                        const s_t = round(s_rate*t/16)*16;
                        const s_len = round(s_rate*80*1.0e-9/16)*16;
                        const s_step = round(s_rate*80*1.0e-9/16)*16;
                        cvar j;                     
                        var i;
                        for (j=0;j<20;j++){{
                          wave w = ones(s_len + j*s_step);
                          assignWaveIndex(1,2,w,j+1);
                        }}
                        while (true){{
                          for (i=0;i<20;i++){{
                            // waitDigTrigger(1);
                            resetOscPhase();
                            setTrigger(1);
                            setTrigger(0);
                            playZero(s_t);
                            executeTableEntry(i+1);
                            waitWave();
                          }}
                        }}
                    """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)

        # Upload command table to instrument
        ct = []
        for i in range(20+1):
            ct.append({
                "index": i,
                "waveform": {
                    "index": i
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
            })
        ct_str = {
            "$schema": "https://docs.zhinst.com/shfsg/commandtable/v1_0/schema#",
            "header": {
                "version": "1.0"
            },
            "table": ct}
        self.daq.setVector(f"/{device_id}/SGCHANNELS/{channel}/AWG/COMMANDTABLE/DATA", json.dumps(ct_str))
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        self.daq.setVector(f"/{device_id}/SGCHANNELS/{channel1}/AWG/COMMANDTABLE/DATA", json.dumps(ct_str))
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/ON", 1)
        # Enable sequencer with single mode
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/ENABLE", 1)

        print(
            f"table2."
        )

    def set_MW_OFF(self):
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 0)


if __name__ == '__main__':
    MW = MW_generater()
    MW.set_parameter(5, 50, 0, 0)
    MW.set_MW_ON_table()
    MW.set_MW_ON()
