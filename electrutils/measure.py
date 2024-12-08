from electrutils.waveform import Wave
import time
import numpy as np
def singleAcq(scp):
    '''
    Sets the oscilloscope up for a single acquisiton, waits for a trigger and returns the waveforms.
    :param scp: The instantiation of a pyMeasure scope (SDS1072CML)
    :return:
        wave: The waveform stored in channel 1
        wave: The waveform stored in channel 2
    '''
    t1,data1= scp.channel_1.get_waveform()
    t2,data2= scp.channel_2.get_waveform()
    wave1 = Wave(t1,data1)
    wave2 = Wave(t2, data2)
    return wave1,wave2


def freqSweep(scp,wvgen,freqs,amplitude,offset=0.,numPeriods=10):
    '''
    Performs a frequency sweep measurement and records the signals read on the oscilloscope
    :param scp: Scope object associated to the oscilloscope used for the experiment
    :param wvgen: Waveform generator object associated to the instrument used for the experiment
    :param freqs: (list of float) List of the frequencies to be swept through in Hz
    :param amplitude: Peak to peak amplitude of the sine wave to be applied  in V
    :return:
    list of ndarray
        A list of all the waveforms measured on CH1
    list of ndarray
        A list of all the waveforms measured on CH2
    '''

    wvgen.channel_1.output_enabled=False
    trig_dict=scp.trigger.get_trigger_config()
    trig_dict['source']='EX'
    trig_dict['level']=0
    trig_dict['mode']='SINGLE'
    trig_dict['slope']='POS'
    scp.trigger.set_trigger_config(**trig_dict)
    scp.channel_1.coupling='AC'
    scp.channel_2.coupling='AC'
    wvgen.channel_1.sync_enabled=True
    waves1=[]
    waves2=[]
    #Check that the yScales are fine
    wvgen.channel_1.sine=freqs[0],amplitude,offset,0
    wvgen.channel_1.output_enabled=True
    pause=0.1
    for freq in freqs:
        # Set the time scale
        period=1./freq
        div=period*numPeriods/18
        scp.time_division=div
        scp.wait(pause)
        time.sleep(pause)
        wvgen.channel_1.frequency=freq
        scp.arm() 
        #time.sleep(np.max([18*div,0.2]))
        print(wvgen.channel_1.waveform)
        scp.wait(pause)
        time.sleep(pause)
        Wave(*scp.channel_1.get_waveform())
        waves1.append(Wave(*scp.channel_1.get_waveform()))
        scp.wait(pause)
        time.sleep(pause)
       # if scp.arm():
       #     print('SCOPE ARMED')
       # #for i in range(3):
       # while not scp.is_ready:
       #     time.sleep(0.01)
       # scp.arm()
        # Ideally, would have afunction call to check if that is the case, but a frequent call to scp.isDone() ends up overfilling the registers and bricking the scope.
        Wave(*scp.channel_2.get_waveform())
        waves2.append(Wave(*scp.channel_2.get_waveform()))
        scp.wait(pause)
        time.sleep(pause)
    wvgen.channel_1.output_enabled=False
    return waves1,waves2