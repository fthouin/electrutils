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
    def setTimeDiv(self,timeDiv,directCommand=None):
        '''
        Sets the time division to the closest possible value,rounding downwards. Available are:
        1NS,2NS,5NS,10NS,20NS,50NS,100NS,200NS,500NS,1US,2US,5US,10US,20US,
        50US,100US,200US,500US,1MS,2MS,5MS,10MS,20MS,50MS,100MS,200MS,500MS,1S,2S,5S,10S,20S,50S
        See page 122 of programming manual
        :param timeDiv: (float) value of the time divisions
        :param directCommand: A string of the time division to get the exact value. For instance, '5NS' or '200MS'
        :return: void
        '''
        if directCommand is None:
            possibleDivs=[1e-9,1e-6,1e-3,1]
            possibleUnits=['N','U','M','']
            unit=''
            indicesSmallerThanTimeDiv=[i for i,div in enumerate(possibleDivs) if timeDiv>div]
            unit=possibleUnits[indicesSmallerThanTimeDiv[-1]]#The last one to have satisfied the condition in the loop is the one we need!
            multiplier=str(int(timeDiv/possibleDivs[indicesSmallerThanTimeDiv[-1]]))
            command = '*TDIV '+multiplier+unit+'S'
            print(command)
        else:
            command = '*TDIV '+directCommand
        self.resource.write(command)

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
    def getINR(self):
        '''
        Gets the scope's Internal state change register and clears it.
        :return:
        '''
        command='*INR?'
        return self.resource.query(command)

    def isDone(self):
        '''
        Checks if the scope is done with it acquisition
        :return:
        '''
        try:
            status = self.getINR()
        except:
            status = 'Communication fault'
        if 'INR 0' in status:
            return True
        else:
            return False

    def isReady(self):
        try:
            status=self.getStatus()
        except:
            status='Communication fault'
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
    def wait(self,time=1):
        '''
        Stops the scope from doing anything until it has completed the current acquisition (p.146)
        :return:
        '''
        command='WAIT %d'%time
        self.resource.write(command)
    def arm(self):
        '''
        Changes the acquisition mode from 'STOPPED' to 'SINGLE'. Useful to ready scope for the next acquisition.
        :return:
        '''
        command='ARM'
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
        '''
        Specifies the amount of data to be sent from the scope to the controller.
        See page 144 of programming manual
        :return: nuttin
        '''
        command='*WFSU SP,0,FP,0'
        self.resource.write(command)

    def getWave(self,channel='C1'):
        descriptor=self.getDesc(channel=channel)
        print(descriptor)
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

