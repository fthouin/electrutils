from sigGen import sigGen
from scope import Scope
import time
from matplotlib import pyplot as plt
scp=Scope()
wvgen=sigGen()
print(scp.getID())
print(wvgen.getID())
scp.setCoupling(channel=1,mode='DC')
scp.setTrig(mode='NORM')
scp.setWaveAcq()
wvgen.setSync()
wvgen.setSine(ampl=1,freq=1000,offset=0.0)
if scp.isReady():
    wvgen.setOutput()
    time.sleep(0.5)
    while not scp.isReady():
        time.sleep(0.001)
    wvgen.setOutput(status=False)
#print(scp.getTemplate())
data,time=scp.getWave(channel='C1')
#print(data)
plt.figure()
plt.plot(time,data,label='Channel 1')
data,time=scp.getWave(channel='C2')
plt.plot(time,data,label='Channel 2')
plt.legend()
plt.show()

wvgen.close()
scp.close()



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