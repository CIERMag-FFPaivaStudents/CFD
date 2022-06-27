#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Program to compare the Poiseuille and Womersley velocity profile in an cardiovascular waveform.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.special import jv

def readFlowRateWaveform(fileName):
    """Reads flow rate waveform from given csv file.

    Parameters
    ----------
    fileName: str
        csv file name containing an interpolated waveform.

    Returns
    -------
    time: array
        Waveform time array
    flowRate: array
        Flow rate array (probably interpolated from waveform features measurements)
    """

    Waveform_df = pd.read_csv(fileName)

    return Waveform_df.get('t').to_numpy(), Waveform_df.get('flow').to_numpy()

def calculatePoiseuille(flowRate, radius, r):
    """Calculate the Poisseuile velocity profile from given waveform flow rate and radius.

    Parameters
    ----------
    flowRate: array
        flow rate array with interpolated waveform.
    radius: float
        radius from specific artery.
    r: array
        radius linear spaced array.

    Returns
    -------
    PoiseuilleProfile: array
        Poiseuille velocity profile for all timepoints in flow rate array.

    """

    PoiseuilleProfile = [2*q/(np.pi*radius**2)*(1-r**2/radius**2) for q in flowRate]

    return PoiseuilleProfile

def calculateWomersley(flowRate, radius, r, period, nu):
    """Calculate the Womersley velocity profile from given waveform and flow parameters.

    Parameters
    ----------
    flowRate: array
        flow rate array with interpolated waveform.
    radius: float
        radius from specific artery.
    r: array
        radius linear spaced array.
    period: float
        period from pulsatile waveform.
    nu: float
        blood dynamic viscosity.

    Returns
    -------
    WormersleyProfile: array
        Womersley velocity profile for all timepoints in flow rate array.

    """

    alpha = np.sqrt(2*np.pi/(nu*period))*radius
    gamma = alpha*(1j-1)/np.sqrt(2)
    
    shapeFunction = (gamma*jv(0,gamma)-
        gamma*jv(0,gamma*r/radius))/(gamma*jv(0,gamma)-
        2*jv(1,gamma))

    WomersleyProfile = np.array([(q/(np.pi*radius**2))*shapeFunction.real for q in flowRate])

    return WomersleyProfile



if __name__=='__main__':

    fileName = 'Ford-YoungAdults-Waveform_ICA.csv'

    radius = 0.015
    period = 1
    nu = 4.5e-4

    r = np.linspace(-radius,radius,200)
   
    t, flowRate = readFlowRateWaveform(fileName)

    PoiseuilleProfile = calculatePoiseuille(flowRate, radius, r)

    WomersleyProfile = calculateWomersley(flowRate, radius, r, period, nu) 


    plt.figure(figsize=(20,10))
    sns.set()
    sns.set_context('talk')
    sns.set_style('ticks')
    plt.subplot(121)
    plt.plot(t,flowRate, color='k')
    plt.scatter(t[0], flowRate[0], color='k')
    plt.scatter(t[1070], flowRate[1070], color='gray', alpha=1)
    plt.scatter(t[3400], flowRate[3400], color='silver', alpha=1)
    plt.xlabel('time (s)')
    plt.ylabel('flow rate ($m^3/s$)')
    plt.subplot(122)
    plt.plot(r, np.array(WomersleyProfile[0]), color = 'k', label='Womersley Profile')
    plt.plot(r, np.array(PoiseuilleProfile[0]), color = 'k', linestyle='dashed', label='Poiseuille Profile')
    plt.plot(r, WomersleyProfile[1070], color = 'gray')
    plt.plot(r, PoiseuilleProfile[1070], color = 'gray', linestyle='dashed')
    plt.plot(r, WomersleyProfile[3400], color = 'silver')
    plt.plot(r, PoiseuilleProfile[3400], color = 'silver', linestyle='dashed')
    plt.xlabel('radius (m)')
    plt.ylabel('velocity (m/s)')
    plt.legend()
    plt.show()
