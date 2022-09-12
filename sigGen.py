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
    def setSine(self,channel=1,freq=100,ampl=2,offset=0,phase=0):
        '''
        Sets the waveform generator to output a sine of specified parameters
        :param channel: (int) The channel number to configure. 1 or 2
        :param freq: (int) The frequency of the sine in Hz
        :param ampl: (float) The peak to peak amplitude of the sine in V
        :param offset: (float) The DC offset of the sine in V
        :param phase: (float) The phase offset of the sine in degrees
        :return:
        '''
        command=r':SOUR%d:APPL:SIN %f,%f,%f,%f?'%(channel,freq,ampl,offset,phase)
        self.resource.write(command)
    def setSync(self,channel=1,status=True):
        '''
        Sets the synchronisation mode of a channel
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

    def setOutput(self,channel=1,status=True):
        if status:
            outputString='ON'
        else:
            outputString='OFF'
        command=r':OUTP%d %s'%(channel,outputString)
        self.resource.write(command)
    def close(self):
        '''
        Gracefully closes the communication
        :return:
        '''
        self.resource.close()
