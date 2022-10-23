from sigGen import sigGen
from scope import Scope
from measure import *
import time
from matplotlib import pyplot as plt
import numpy as np
scp=Scope()
wvgen=sigGen()
print(scp.getID())
print(wvgen.getID())
scp.setCoupling(channel=1,mode='DC')
scp.setTrig(mode='SINGLE')
scp.setWaveAcq()
scp.setTimeDiv(timeDiv=75e-6)
wvgen.setSync()
wvgen.setSine(ampl=1,freq=1000,offset=0.0)
time.sleep(0.15)
print('INR 1')
print(scp.getINR()=='0')
scp.arm()
wvgen.setOutput()
print('INR 2')
print(scp.getINR()=='0')
time.sleep(0.15)
#print(scp.getTemplate())
data1,t1=scp.getWave(channel='C1')
print('INR 3')
print(scp.getINR())
print('0' in scp.getINR())
time.sleep(0.15)
data2,t2=scp.getWave(channel='C2')
wvgen.setOutput(status=False)
scp.arm()
#print(data)
plt.figure()
plt.plot(t1,data1,label='Channel 1')
plt.plot(t2,data2,label='Channel 2')
plt.legend()
print()
#wave1,wave2=freqSweep(scp,wvgen,np.logspace(2,4,100),0.2,numPeriods=10)
#plt.figure()
#for i,wave in enumerate(wave1):
#    print(i)
#    plt.plot(wave)
wvgen.close()
scp.close()

plt.show()


#import pyvisa
#rm=pyvisa.ResourceManager('@py')
#resList=rm.list_resources()
#print(resList)
#scope=None
#waveGen=None
#for resID in resList:
#    if 'SDS' in resID:
#        print('Found the SDS1072CML scope. Connected to it.')
#        scope=rm.open_resource(resID)
#    if 'DG8' in resID:
#        print('Found waveform generator. Connected to it.')
#        waveGen=rm.open_resource(resID)

#if resList !=():
#    scope= rm.open_resource("USB0::6833::1603::DG8A224503800::0::INSTR")
#    print(scope.query("*IDN?"))
#    scope.close()