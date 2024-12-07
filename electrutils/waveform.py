import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft,fftfreq
from scipy.signal import windows
from electrutils.electrools import todBAmp
class Wave:

    def __init__(self,data,t):
        self.t=t
        self.data=data
        self.N = len(self.t)
        self.dt=self.t[1]-self.t[0]

    def getSpectrum(self):
        '''
        Fourier transforms the waveform
        :return:
        '''
        try:
            w=windows.hann(self.N)
        except AttributeError:
            self.N = len(self.t)
            self.dt = self.t[1] - self.t[0]
        finally:
            w=windows.hann(self.N)
            spectrum=2.0/self.N*fft(self.data*w)
            f=fftfreq(self.N,self.dt)
            f=f[:self.N//2]
        return f,spectrum
    def getPositiveSpectrum(self):
        '''
        Gets the positive frequency part of the spectrum
        :return:
        '''
        f,s=self.getSpectrum()
        f=f[1:self.N//2]
        s=s[1:self.N//2]
        return f,s
    def plotSpectrum(self,axs=None,coord='polar',label=None):
        '''
        Plots the spectrum of the waveform
        :param fig: Figure in which to plot the spectrum
        :param coord: Coordinates in which to plot. By default, polar (R, phi) is used
        :return:
        '''
        if axs is None:
            fig,axs=plt.subplots(2,1,sharex='col')
        f,s=self.getPositiveSpectrum()
        magnitude=todBAmp(np.abs(s))
        axs[0].plot(f,magnitude,label=label)
        axs[0].set_ylabel('R (dBV)')
        axs[1].plot(f[magnitude>-80],np.angle(s[magnitude>-80],deg=True),'d')
        axs[1].set_ylabel('$\phi$')
        axs[1].set_xlabel('Frequency (Hz)')
        axs[0].set_xscale('log')
        [ax.grid(which='Major', linestyle='-') for ax in axs]
        [ax.grid(which='Minor', linestyle=':') for ax in axs]
        return axs
    def plotData(self,axs=None,label=None):
        '''
        Plots the data in time in the specified axes. If none are specified, a new figure is made
        :param axs:
        :return:
        '''
        if axs is None:
            fig, axs = plt.subplots(1, 1)
        axs.plot(1000*np.array(self.t),self.data,label=label)
        axs.set_xlabel('Time since epoch [ms]')
        axs.set_ylabel('Voltage [V]')
        axs.grid(which='Major', linestyle='-')
        axs.grid(which='Minor', linestyle=':')
        return axs
