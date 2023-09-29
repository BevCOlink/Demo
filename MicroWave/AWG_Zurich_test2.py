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
channel1 = 1


class MW_generater():
    def __init__(self):
        # connect device
        self.daq = zhinst.ziPython.ziDAQServer(host=server_host, port=server_port, api_level=6)
        self.daq.connectDevice(device_id, interface)
        print(zhinst.utils.api_server_version_check(self.daq))

    def set_parameter(self, rflf_path, mw_power, mw_frequency, mw_pulse_length, rflf_path1, rf_power, rf_frequency,
                      start_time, stop_time, points, step):
        synth_nmbr = self.daq.getInt(f"/{device_id}/SGCHANNELS/{channel}/SYNTHESIZER")
        synth_nmbr1 = self.daq.getInt(f"/{device_id}/SGCHANNELS/{channel1}/SYNTHESIZER")
        # Turn on output
        # self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 1)
        # Set SHFSG to use RF path (in case LF path was enabled earlier)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/RFLFPATH", rflf_path)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/RFLFPATH", rflf_path1)
        # Set RF center frequency
        if rflf_path == 1:
            self.daq.setDouble(
                f"/{device_id}/SYNTHESIZERS/{synth_nmbr}/CENTERFREQ", mw_frequency * 1e6
            )
        else:
            self.daq.setDouble(f"/dev12151/sgchannels/{channel}/digitalmixer/centerfreq", mw_frequency * 1e6)
        if rflf_path1 == 1:
            self.daq.setDouble(
                f"/{device_id}/SYNTHESIZERS/{synth_nmbr1}/CENTERFREQ", rf_frequency * 1e6
            )
        else:
            self.daq.setDouble(f"/dev12151/sgchannels/{channel1}/digitalmixer/centerfreq", rf_frequency * 1e6)
        # Set power in dBm, in steps of 5dBm
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/RANGE", mw_power)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/RANGE", rf_power)

        ## Configure digital modulation
        # Set modulation frequency
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/OSCS/0/FREQ", 10 * 1e6)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/OSCS/0/FREQ", 10 * 1e6)
        # Set sine generator
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/OSCSELECT", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/OSCSELECT", 0)
        # Set harmonic of sine generator
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/HARMONIC", 1)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/HARMONIC", 1)
        # Set phase of sine generator
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/SINES/0/PHASESHIFT", 0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/SINES/0/PHASESHIFT", 0)
        # Gains
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/0/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/0/gains/1", -1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/1/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/outputs/1/gains/1", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/AWG/outputs/0/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/AWG/outputs/0/gains/1", -1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/AWG/outputs/1/gains/0", 1.0)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/AWG/outputs/1/gains/1", 1.0)
        # Global Amplitude
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel}/AWG/OUTPUTAMPLITUDE", 0.5)
        self.daq.setDouble(f"/{device_id}/SGCHANNELS/{channel1}/AWG/OUTPUTAMPLITUDE", 0.5)
        # Enable digital modulation
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/MODULATION/ENABLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/MODULATION/ENABLE", 1)

        # Set marker source
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/MARKER/SOURCE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/MARKER/SOURCE", 0)

        self.t = mw_pulse_length
        self.a = start_time
        self.b  = stop_time
        self.n = points
        self.s = step

    def set_MW_ON(self):    # run time defined
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/ENABLE", 0)
        self.daq.sync()
        awg_seqc = f"""
                const s_rate = 2.0e9;
                const t = {self.t}*1.0e-9;
                const s_t = round(s_rate*t/16)*16;
                const t_wait = {self.b}*1.0e-9;
                const s_wait = round(s_rate*t_wait/16)*16;
                wave w = ones(s_t);
                assignWaveIndex(1,2,w,1,2,w,0);
                while (true){{
                  waitDigTrigger(1);
                  resetOscPhase();
                  setTrigger(1);
                  setTrigger(0);
                  executeTableEntry(0);
                  playZero(s_wait);
                  executeTableEntry(0);
                }}
            """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)
        awg_seqc1 = f"""
                        const s_rate = 2.0e9;
                        const t = {self.t}*1.0e-9;
                        const s_t = round(s_rate*t/16)*16;                       
                        var i;
                        while (true){{
                          const s_len = round(s_rate*{self.a}*1.0e-9/16)*16;
                          const s_step = round(s_rate*{self.s}*1.0e-9/16)*16;
                          for (i=0;i<{self.n};i++){{
                            wave w = ones(s_len);
                            waitDigTrigger(1);
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
        common_shfsg.load_sequencer_program(self.daq, device_id, channel1, awg_seqc1)

        # Upload command table to instrument
        ct = [
            {
                "index": 0,
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
        self.daq.setVector(f"/{device_id}/SGCHANNELS/{channel1}/AWG/COMMANDTABLE/DATA", json.dumps(ct_str))
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/ON", 1)
        # Enable sequencer with single mode
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/SINGLE", 1)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/ENABLE", 1)

        print(
            f"Rabi sequence with frequency generated on channel."
        )

    def set_MW_ON2(self):   # table, predefined
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/ENABLE", 0)
        self.daq.sync()
        awg_seqc = f"""
                const s_rate = 2.0e9;
                const t = {self.t}*1.0e-9;
                const s_t = round(s_rate*t/16)*16;
                const t_wait = {self.b}*1.0e-9;
                const s_wait = round(s_rate*t_wait/16)*16;
                wave w = ones(s_t);
                assignWaveIndex(1,2,w,1,2,w,0);
                while (true){{
                  waitDigTrigger(1);
                  resetOscPhase();
                  setTrigger(1);
                  setTrigger(0);
                  executeTableEntry(0);
                  playZero(s_wait);
                  executeTableEntry(0);
                }}
            """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel, awg_seqc)
        awg_seqc1 = f"""
                        const s_rate = 2.0e9;
                        const t = {self.t}*1.0e-9;
                        const s_t = round(s_rate*t/16)*16;
                        const s_len = round(s_rate*{self.a}*1.0e-9/16)*16;
                        const s_step = round(s_rate*{self.s}*1.0e-9/16)*16;
                        cvar j;                     
                        var i;
                        for (j=0;j<{self.n};j++){{
                          wave w = ones(s_len + j*s_step);
                          assignWaveIndex(1,2,w,j+1);
                        }}
                        while (true){{
                          for (i=0;i<{self.n};i++){{
                            waitDigTrigger(1);
                            resetOscPhase();
                            setTrigger(1);
                            setTrigger(0);
                            playZero(s_t);
                            executeTableEntry(i+1);
                            waitWave();
                          }}
                        }}
                    """
        common_shfsg.load_sequencer_program(self.daq, device_id, channel1, awg_seqc1)

        # Upload command table to instrument
        ct = []
        for i in range(self.n+1):
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
            f"Rabi sequence with frequency generated on channel."
        )

    def set_MW_OFF(self):
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel}/OUTPUT/ON", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/AWG/ENABLE", 0)
        self.daq.setInt(f"/{device_id}/SGCHANNELS/{channel1}/OUTPUT/ON", 0)


if __name__ == '__main__':
    MW = MW_generater()

