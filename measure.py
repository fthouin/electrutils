from sigGen import sigGen
from scope import Scope
import time
from waveform import Wave
def singleAcq(scp,channels='both'):
    '''
    Sets the oscilloscope up for a single acquisiton, waits for a trigger and returns the waveforms.
    :param scp:
    :return:
        wave: The waveform stored in channel 1
        wave: The waveform stored in channel 2
    '''
#    scp.setTrig(mode='SINGLE')
#    scp.setWaveAcq()
#    scp.stop()
#    scp.arm()
#    print('SCOPE ARMED')
#    #scp.wait()
#    while not scp.isReady():
#        print('chillin')
#        time.sleep(100e-3)
    if channels=='both':
        data1, t1 = scp.getWave(channel='C1')
        data2, t2 = scp.getWave(channel='C2')
        wave1 = Wave(data1, t1)
        wave2 = Wave(data2, t2)
    elif channels=='C1':
        data1, t1 = scp.getWave(channel='C1')
        wave1 = Wave(data1, t1)
        wave2 = None
    elif channels=='C2':
        data2, t2 = scp.getWave(channel='C2')
        wave2 = Wave(data2, t2)
        wave1 = None

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
    scp.setCoupling(channel=1, mode='AC')
    scp.setCoupling(channel=2, mode='AC')
    scp.setTrig(mode='SINGLE',source='EX')
    scp.setWaveAcq()
    wvgen.setSync(channel=1,status=True)
    wave1=[]
    wave2=[]
    #Check that the yScales are fine
    wvgen.setOutput()
    print('OUTPUT IS ON')
    wvgen.setSine(ampl=amplitude, offset=offset)
    print('GETTING WAVE1')
    scp.wait()
    scp.getWave(channel='C1')
    print('GETTING WAVE2')
    scp.getWave(channel='C2')
    #scp.wait()
    for freq in freqs:
        # Set the time scale
        period=1./freq
        div=period*numPeriods/18
        scp.setTimeDiv(timeDiv=div)
        wvgen.setFrequency(channel=1,freq=freq)
        print(wvgen.queryWaveform())
        print('TIMEDIVSET')
        print('FREQ OUTPUT SET')
        print('%.2e Hz'%freq)
        #time.sleep(2)
        scp.stop()
        scp.wait()
        scp.arm()
        print('SCOPE ARMED')
        #time.sleep(10*numPeriods*period+0.1)# Wait for the acquisition to be over.
        # Ideally, would have afunction call to check if that is the case, but a frequent call to scp.isDone() ends up overfilling the registers and bricking the scope.
        print('GETTING WAVE1')
        data1, t1 = scp.getWave(channel='C1')
        print('GETTING WAVE2')
        data2, t2 = scp.getWave(channel='C2')
        print('APPENDING')
        wave1.append(Wave(data1,t1))
        wave2.append(Wave(data2,t2))
    wvgen.setOutput(status=False)
    return wave1,wave2