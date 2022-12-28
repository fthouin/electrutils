import numpy as np

def todBAmp(x):
    '''
        Converts an amplitude ratio to decibels using dBV=20log10(R)
    '''
    db=20*np.log10(x)
    return db
