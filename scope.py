import pyvisa
import struct

class Scope:
    idString='SDS'
    def __init__(self):
        '''
        Connect to the SDS scope by scanning the ressources seen by PyVisa
        Check that the scope is set to USBTMC mode in its Utility menu.
        '''
        rm=pyvisa.ResourceManager('@py')
        resList=rm.list_resources()
        for resID in resList:
            if Scope.idString in resID:
                print('Found the SDS1072CML scope. Connected to it.')
                self.resource = rm.open_resource(resID)
                self.resource.read_termination = '\n'
    def getID(self):
        '''
        Queries the ID of the device
        :return:
            str
            The message returned by the device
        '''
        return self.resource.query('*IDN?')
    def getStatus(self):
        '''
        Queries the sampling status of the scope
        :return: a str that is either
            'SAST Stop'
            'SAST Ready'
            'SAST Trig'd'
            'SAST Armed'
        '''
        return self.resource.query('SAST?')
    def isReady(self):
        status=self.getStatus()
        if 'Ready' in status or 'Armed' in status:
            return True
        else:
            return False
    def setCoupling(self,channel=1,mode='DC'):
        '''
        Sets the channel coupling mode. (see UM p. 35)
        :param channel: (int) the channel to be configured
        :param mode: (str) sets the coupling to DC ('DC', default) or AC ('AC')
        :return:
        '''
        if mode=='AC':
            outputString='A1M'
        else:
            outputString='D1M'
        command=r'C%d:CPL %s'%(channel,outputString)
        self.resource.write(command)
    def setTrig(self,source='EX',type='EDGE',level=1,coupling='DC',mode='NORM',slope='POS'):
        '''
        Sets up the trigger parameters
        :param source: (str, {EX,EX/5,C1,C2}) Channel from which to get the trigger signal from
        :param type: (str,{EDGE,TV}) Sets the trigger type. Many more available see page 131 of ProgMan.
        :param level: (float) Trigger level in volts.
        :param coupling: (str,{AC,DC}) Coupling to the trigger channel
        :param mode: (str, {NORM, AUTO, SINGLE}) Sets the behavior of the trigger following events
        :param slope: (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.
        :return:
        '''
        command='TRSE %s,SR,%s,HT,TI'%(type,source)
        self.resource.write(command)
        command='TRMD %s'%(mode)
        self.resource.write(command)
        command='%s:TRLV %f'%(source,level)
        self.resource.write(command)
        command='%s:TRCP %s'%(source,coupling)
        self.resource.write(command)
        command='%s:TRSL %s'%(source,slope)
        self.resource.write(command)
    def setWaveAcq(self):
        command='*WFSU SP,0,FP,0'
        self.resource.write(command)

    def getWave(self,channel='C1'):
        descriptor=self.getDesc(channel=channel)
        descriptorOffset=21#Length of the C1:WF ALL,#9000000346 message
        #print(struct.unpack_from('21s8s8x3s13x',descriptor))
        (numDataPoints,)=struct.unpack_from('l',descriptor,offset=descriptorOffset+60)
        (verticalGain,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+156)
        (verticalOffset,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+160)
        (horizInterval,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+176)
        (horizOffset,)=struct.unpack_from('d',descriptor,offset=descriptorOffset+180)
        print(horizOffset)
        command='%s:WF? DAT2'%channel
        self.resource.write(command)
        response=self.resource.read_raw()
        data= struct.unpack_from('%db'%numDataPoints,response,offset=descriptorOffset)
        data=list(data)
        data=[point*verticalGain-verticalOffset for point in data]
        time=[i*horizInterval+horizOffset for i in range(len(data))]
        return data,time
    def getDesc(self,channel='C1'):
        '''
        Gets the descriptor of data being sent when querying device for waveform
        :return:
        '''
        command='%s:WF? DESC'%channel
        self.resource.write(command)
        return self.resource.read_raw()
    def getTemplate(self):
        '''
        Gets the template of data being sent when querying device for waveform
        :return:
        '''
        command='TEMPLATE?'
        return self.resource.query(command)

    def close(self):
        '''
        Gracefully closes the communication
        :return:
        '''
        self.resource.close()

