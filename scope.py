import time
import pyvisa
import struct
class Scope:
    idString='SDS'
    def __init__(self):
        '''
        Connect to the SDS scope by scanning the ressources seen by PyVisa
        Check that the scope is set to USBTMC mode in its Utility menu.
        '''
        time.sleep(0)
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
        return self.getTimeDiv()
    def getTimeDiv(self):
        '''
        Returns the current time division
        :return:
        the current time division. See page 122
        '''
        command = 'TDIV?'
        return self.resource.query(command)

    def getStatus(self):
        '''
        Queries the sampling status of the scope
        :return: a str that is either
            'SAST Stop'
            'SAST Ready'
            'SAST Trig'd'
            'SAST Armed'
        '''

        self.resource.write('SAST?')
        status=None
        numCalls=0
        while status is None and numCalls<1000:
            try:
                status=self.resource.read()
            except:
                numCalls=numCalls+1
            time.sleep(0.001)
        if status is None:
            status='No answer from ressource (scope)'
        return status
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
        '''
        Checks if the scope is Ready for the next acquisition.
        :return:
        bool: true if the scope is ready.
        '''
        #try:
        #    status=self.getStatus()
        #except:
        #    status='Communication fault'
        status = self.getStatus()
        if 'Stop' in status:
            return True
        else:
            #print(status)
            return False
    def stop(self):
        '''
        Stops all acquisitions!
        :return:
        '''
        command='STOP'
        self.resource.write(command)
        return self.getStatus()

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
        return self.getCoupling(channel=channel)

    def getCoupling(self,channel=1):
        '''
        Gets the channel's coupling mode. (see UM p. 35)
        :param channel: (int) the channel to be queried (default is 1)
        :return:
        '''
        command=r'C%d:CPL?'%(channel)
        coupling=self.resource.query(command)
        return coupling

    def comDelay(self):
        '''
        Sets a buffer time to be executed after write commands

        :return:
        '''
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
        #return self.getStatus()

    def setTrig(self,source=None,type='EDGE',level=None,coupling=None,mode=None,slope=None):
        '''
        Sets up the trigger parameters
        :param source: (str, {EX,EX/5,C1,C2}) Channel from which to get the trigger signal from
        :param type: (str,{EDGE,TV}) Sets the trigger type. Many more available see page 131 of ProgMan.
        :param level: (float) Trigger level in volts.
        :param coupling: (str,{AC,DC}) Coupling to the trigger channel
        :param mode: (str, {NORM, AUTO, SINGLE}) Sets the behavior of the trigger following events
        :param slope: (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.
        Setting any of these parameters to None leaves them unchanged
        :return:
        '''
        if source is not None:
            if type is not None:
                command='TRSE %s,SR,%s,HT,TI'%(type,source)
                self.resource.write(command)
                self.getTrigMode()  # Ca a lair complique de mettre un string de retour pertinent alors cest juste pour
            if level is not None:
                command='%s:TRLV %f'%(source,level)
                self.resource.write(command)
                self.getTrigMode()  # Ca a lair complique de mettre un string de retour pertinent alors cest juste pour
            if coupling is not None:
                command = '%s:TRCP %s' % (source, coupling)
                self.resource.write(command)
                self.getTrigMode()  # Ca a lair complique de mettre un string de retour pertinent alors cest juste pour
            if slope is not None:
                command = '%s:TRSL %s' % (source, slope)
                self.resource.write(command)
                self.getTrigMode()  # Ca a lair complique de mettre un string de retour pertinent alors cest juste pour
            if all([variable is None for variable in [slope,coupling,level,type]]):
                print('Trigger source specified without any atttribute.')
                print('|-> No trigger source related settings applied')
        if any([variable is not None for variable in [slope, coupling, level, type]]) and source is None :
            print('Attributes specified without any trigger source.')
            print('|-> No trigger source related settings applied')
        if mode is not None:
            command='TRMD %s'%(mode)
            self.resource.write(command)
        self.getTrigMode()# Ca a lair complique de mettre un string de retour pertinent alors cest juste pour
        # attendre que la commande d<avant soit termine
    def getTrigMode(self):
        '''
        Gets the trigger mode parameters
        :return: A string describing the trigger mode (see p. 131)

        '''
        command = 'TRMD?'
        self.resource.query(command)
    def getWaveAcq(self):
        '''
        Queries the amount of data to be sent from the scope to the controller.
        See page 144 of programming manual
        :return: nuttin
        '''
        command='WFSU?'
        return self.resource.query(command)
    def setWaveAcq(self):
        '''
        Specifies the amount of data to be sent from the scope to the controller.
        See page 144 of programming manual
        :return: nuttin
        '''
        command='*WFSU SP,0,FP,0'
        self.resource.write(command)
        return self.getWaveAcq()

    def getWave(self,channel='C1'):
        '''
        Recovers the waveforms in the oscilloscope
        :param channel: the channel from which to get the waveform
        :return:
            list of float: the data contained in the waveform
            list of float: the time associated with each point since the trigger event
        '''
        import time
        while not self.isReady():
            time.sleep(0.005)
        descriptor=self.getDesc(channel=channel)
        descriptorOffset=21#Length of the C1:WF ALL,#9000000346 message
        #print(struct.unpack_from('21s8s8x3s13x',descriptor))
        (numDataPoints,)=struct.unpack_from('l',descriptor,offset=descriptorOffset+60)
        (verticalGain,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+156)
        (verticalOffset,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+160)
        (horizInterval,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+176)
        (horizOffset,)=struct.unpack_from('d',descriptor,offset=descriptorOffset+180)
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

