import pyvisa
class sigGen:
    idString='DG8'
    def __init__(self):
        '''
        Connect to the SDS scope by scanning the ressources seen by PyVisa
        Check that the scope is set to USBTMC mode in its Utility menu.
        '''
        rm=pyvisa.ResourceManager('@py')
        resList=rm.list_resources()
        for resID in resList:
            if sigGen.idString in resID:
                print('Found the DG822 signal generator. Connected to it.')
                self.resource = rm.open_resource(resID)
    def getID(self):
        '''
        Queries the ID of the device
        :return:
            str
            The message returned by the device
        '''
        return self.resource.query('*IDN?')
    def getOutputStatus(self,channel=1):
        '''
        Queries the output state of a channel on the device
        :return:
            bool
            True if the channel is on and False if not
        '''
        command=r':OUTP%d?'%channel
        return self.resource.query(command)

    def setFrequency(self,channel=1,freq=100):
        '''
        Sets the output frequency of a given channel.
        :param channel: (int) The channel number to configure. 1 or 2
        :param freq: (int) The frequency of the sine in Hz
        :return:
        '''
        command=r':SOUR%d:FREQ %f'%(channel,freq)
        self.resource.write(command)
        return self.getFrequency()
    def getFrequency(self,channel=1):
        '''
        Gets the output frequency of a given channel.
        :param channel: (int) The channel number to configure. 1 or 2
        :return:
        str: the frequency of the channel
        '''
        command=r':SOUR%d:FREQ?'%(channel)
        return self.resource.query(command)

    def setSine(self,channel=1,freq=100,ampl=2,offset=0,phase=0):
        '''
        Sets the waveform generator to output a sine of specified parameters
        :param channel: (int) The channel number to configure. 1 or 2
        :param freq: (int) The frequency of the sine in Hz
        :param ampl: (float) The peak to peak amplitude of the sine in V
        :param offset: (float) The DC offset of the sine in V
        :param phase: (float) The phase offset of the sine in degrees
        :return:
        str:the waveform type as wel as its frequency, amplitude, phase and offset
        '''
        command=r':SOUR%d:APPL:SIN %f,%f,%f,%f?'%(channel,freq,ampl,offset,phase)
        self.resource.write(command)
        return self.queryWaveform()
    def queryWaveform(self,channel=1):
        '''
        Queries the waveform being output by the generator
        '''
        command=r':SOUR%d:APPL?'%(channel)
        response=self.resource.query(command)
        return response

    def setSync(self,channel=1,status=True):
        '''
        Sets the synchronisation mode of a channel, enabling or disabling the trigger output
        :param channel: (int) the channel to be configured
        :param status: (bool) selected wether to enable (True) or disable (False) the sync
        :return:
        '''
        if status:
            outputString = 'ON'
        else:
            outputString = 'OFF'
        command=r':OUTP%d:SYNC %s'%(channel,outputString)
        self.resource.write(command)
        return self.getSync()
    def getSync(self,channel=1):
        '''
        Queries the status of the channel's SYNC output
        :param channel:1 or 2
        :return:
        The status of the channel<s sync output (str)
        '''
        command=r':OUTP%d:SYNC?'%(channel)
        return self.resource.query(command)

    def setOutput(self,channel=1,status=True):
        '''
        Sets the output of the specified channel ON or OFF
        :param channel: the channel to set
        :param status: the desired status. True (bool) for On
        :return:
        :param status: the channel's status after the operation
        '''
        if status:
            outputString='ON'
        else:
            outputString='OFF'
        command=r':OUTP%d %s'%(channel,outputString)
        self.resource.write(command)
        return self.getOutput()
    def getOutput(self,channel=1):
        '''
        Gets the output of the specified channel ON or OFF
        :param channel: the channel to set
        :return:
        :param status: the channel's status
        '''
        command=r':OUTP%d?'%(channel)
        return self.resource.query(command)

    def close(self):
        '''
        Gracefully closes the communication
        :return:
        '''
        self.resource.close()
