#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Unscented kalman filter parameter estimation. Algorithm from: https://filterpy.readthedocs.io/en/latest/. Synthetic flow and pressure from https://doi.org/10.1002/cnm.2692.

"""
import numpy as np
import seaborn as sns
from copy import deepcopy
import matplotlib.pyplot as plt
from numpy import dot, zeros, eye, outer
from numpy.random import multivariate_normal
from filterpy.kalman import MerweScaledSigmaPoints
from filterpy.kalman import UnscentedKalmanFilter as UKF

def applyMultipleCycles(T, V, n_cycle, period):
    """Get the waveform and repeats it for a desired number of cycles (without fisiological variation).
    
    Parameters
    ----------
    T: array
        Time points relative to time of mid-acceleration.
    V: array
        Normalized volumetric flow rate values feature points.
    n_cycle: int
        Desired number of cycles for tile operation.
    period: float
        Period of the waveform feature points.

    Returns
    -------
    T_cycle: array
        Time points repeated for a given period and number of cycles.
    V_cycle:
        Normalized volumetric flow rate feature points for a given period and number of cycles.

    """

    V_cycle = np.tile(V, n_cycle)
    T_cycle = np.array([[n*period+t for t in T] for n in range(n_cycle)]).reshape(-1)

    return T_cycle, V_cycle

def calculatePressure(t, flow, Rd, Rp, C, p0):
    """Calculate the pressure waveform at boundary from flow rate waveform, compliance, integration constant, and resistance (distal and proximal).

    Parameters
    ----------
    t: array
        Waveform time array.
    flow: array
        Flow rate array (probably interpolated from waveform features measurements)

    Returns
    -------
    p: array

    """
    tau = Rd*C
    Q0 = flow[0]
    dt = t[1]-t[0]
    p = []

    for i in range(len(t)):
        if i==0:
            p.append(p0*(1-dt/tau)+Rp*flow[i]+flow[i]*(Rd+Rp)*dt/tau)
        else:
            p.append(p[i-1]*(1-dt/tau)+Rp*(flow[i]-flow[i-1])+flow[i]*(Rd+Rp)*dt/tau)

    return p

def observation(sigma_point_minus):
    H = np.array([1, 0, 0, 0])
    observed_sigma = H*sigma_point_minus
    return observed_sigma

def pressureDynamics(sigmaPoint, dt, flowInput, x_ref):

    p_i = x_ref[0]*2**sigmaPoint[0]
    Rp = x_ref[1]*2**sigmaPoint[1]
    C = x_ref[2]*2**sigmaPoint[2]
    Rd =  x_ref[3]*2**sigmaPoint[3]
    tau = Rd*C

    flow_i = flowInput[1]
    flow_im1 = flowInput[0]

    p = p_i*(1-dt/tau)+Rp*(flow_i-flow_im1)+flow_i*(Rd+Rp)*dt/tau

    sigmaPoint[0] = np.log(p/x_ref[0])/np.log(2)


    return sigmaPoint

if __name__=='__main__':

    mu = 0.35
    sigma = 0.05
    flow_amplitude = 10
    flow_offset = 5
    t = np.arange(0,0.8, 0.005)
    flow = flow_offset+flow_amplitude*np.exp(-np.power(t-mu, 2)/(2*np.power(sigma,2)))

    t_multiple, flow_multiple = applyMultipleCycles(t, flow, 10, 0.8)
    dt = t_multiple[1]-t_multiple[0]

    #windkessel parameters
    Rp = 1600
    C = 2.5e-5
    Rd = 13000
    p0 = 80000

    p = calculatePressure(t_multiple, flow_multiple, Rd, Rp, C, p0)

    p += np.random.normal(0, 1600, len(flow_multiple))

    #initial guess
    pressure = 80000
    Rp_guess = 1000
    C_guess = 1e-5
    Rd_guess = 12000

    x_ref = np.array([pressure, Rp_guess, C_guess, Rd_guess])

    size_n = np.array(p).shape[0]

    x = np.zeros(x_ref.shape[0])

    sigmas = MerweScaledSigmaPoints(n=x.shape[0], alpha = 1e-2, beta = 2., kappa = 0.)
    ukf = UKF(dim_x = x.shape[0], dim_z = 1, dt=dt, points = sigmas,
            hx = observation, fx = pressureDynamics)
    ukf.x = x
    ukf.R = 0.01*np.eye(x.shape[0])
    ukf.Q = 0.0001*np.eye(x.shape[0])
    
    uxs=[]
    uxs_std = []
    for i in range(size_n):
        if i==0:
            flowInput = [flow_multiple[0], flow_multiple[0]]
        else:
            flowInput = [flow_multiple[i-1], flow_multiple[i]]

        z = [np.log(p[i]/x_ref[0])/np.log(2), ukf.x[1], ukf.x[2], ukf.x[3]]

        ukf.predict(**{'flowInput':flowInput, 'x_ref':x_ref})
        ukf.update(z)
        uxs.append(ukf.x.copy())
        uxs_std.append([ukf.P[0,0], ukf.P[1,1], ukf.P[2,2], ukf.P[3,3]])


    uxs=np.array(uxs)
    uxs_std=np.array(uxs_std)
    fig, ax = plt.subplots(2,2)
    ax[0,0].plot(t_multiple,p*1e-3, color='k')
    ax[0,0].plot(t_multiple,x_ref[0]*2**(uxs[:,0])*1e-3, color='gray')
    ax[0,0].fill_between(t_multiple,
            x_ref[0]*2**(uxs[:,0]+uxs_std[:,0])*1e-3,x_ref[0]*2**(uxs[:,0]-uxs_std[:,0])*1e-3,
         color='gray', alpha=0.5)
    ax[0,0].set_ylim([60, 150])
    ax[0,0].set_ylabel('Pressure (mmHg)')
    ax[0,0].set_xlabel('t (s)')
    ax[0,1].plot(t_multiple, x_ref[1]*2**(uxs[:,1]), color='gray')
    ax[0,1].plot(t_multiple, Rp*np.ones(len(p)), linestyle='--', color='k')
    ax[0,1].fill_between(t_multiple,
            x_ref[1]*2**(uxs[:,1]+uxs_std[:,1]),x_ref[1]*2**(uxs[:,1]-uxs_std[:,1]),
         color='gray', alpha=0.5)
    ax[0,1].set_ylim([300, 5000])
    ax[0,1].set_ylabel('$R_p$ (dyne-s/$cm^5$)')
    ax[0,1].set_xlabel('t (s)')
    ax[1,0].plot(t_multiple, x_ref[2]*2**(uxs[:,2]), color= 'gray')
    ax[1,0].plot(t_multiple, C*np.ones(len(p)), linestyle='--', color='k')
    ax[1,0].fill_between(t_multiple,
            x_ref[2]*2**(uxs[:,2]+uxs_std[:,2]),x_ref[2]*2**(uxs[:,2]-uxs_std[:,2]),
         color='gray', alpha=0.5)
    ax[1,0].set_ylim([2e-6, 4e-5])
    ax[1,0].set_ylabel('C ($cm^5$/dyne)')
    ax[1,0].set_xlabel('t (s)')
    ax[1,1].plot(t_multiple,x_ref[3]*2**(uxs[:,3]), color='gray')
    ax[1,1].fill_between(t_multiple,
            x_ref[3]*2**(uxs[:,3]+uxs_std[:,3]),x_ref[3]*2**(uxs[:,3]-uxs_std[:,3]),
         color='gray', alpha=0.5)
    ax[1,1].plot(t_multiple, Rd*np.ones(len(p)), linestyle='--', color='k')
    ax[1,1].set_ylim([4000, 50000])
    ax[1,1].set_ylabel('$R_d$ (dyne-s/$cm^5$)')
    ax[1,1].set_xlabel('t (s)')
    plt.show()

