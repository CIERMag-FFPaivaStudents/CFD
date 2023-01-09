#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Ensemble kalman filter parameter estimation. Implementation of algorithm described in: https://filterpy.readthedocs.io/en/latest/. Synthetic flow and pressure from  https://doi.org/10.1002/cnm.2692.

"""
import numpy as np
import seaborn as sns
from copy import deepcopy
import matplotlib.pyplot as plt
from numpy import dot, zeros, eye, outer
from numpy.random import multivariate_normal

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


def pressureDynamics(p_i, dt, Rp, C, Rd, flowInput):
    
    tau = Rd*C

    flow_i = flowInput[1]
    flow_im1 = flowInput[0]

    p = p_i*(1-dt/tau)+Rp*(flow_i-flow_im1)+flow_i*(Rd+Rp)*dt/tau

    return p


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

    size_n = np.array(p).shape[0]

    P = 0.25*np.eye(3)
    R = 0.01#*np.eye(3)
    Q = 0.0001*np.eye(3)

    N=100
    
    x_ini = np.array([Rp_guess, C_guess, Rd_guess])
    thetas = multivariate_normal(mean=np.zeros(3), cov=P, size=N)
    theta = np.mean(thetas, axis=0)
    previous_pressure = pressure*np.ones(N)

    uxs = []
    uxs_std=[]
    zs = []
    zs_std=[]

    for i in range(size_n):
        if i==0:
            flowInput = [flow_multiple[0], flow_multiple[0]]
        else:
            flowInput = [flow_multiple[i-1], flow_multiple[i]]

        tau = multivariate_normal(mean=np.zeros(3), cov=Q, size=N)

        thetas += tau

        y = np.zeros((N,1))
        for j in range(N):
            y[j] = pressureDynamics(previous_pressure[j], dt,
                    x_ini[0]*2**thetas[j,0], 
                    x_ini[1]*2**thetas[j,1], 
                    x_ini[2]*2**thetas[j,2], flowInput)

        y_mean = np.mean(y, axis=0)
        previous_pressure = np.copy(y)

        e_r = np.random.normal(0,0.05*p[i], N)
        R = np.dot(e_r, e_r.transpose())/(N-1)

        P_yy = 0
        for y_i in y:
            s = y_i-y_mean
            P_yy +=outer(s, s)
        P_yy = P_yy / (N-1) + R
        
        P_xy = 0
        for j in range(N):
            P_xy += outer(thetas[j] - theta, y[j] - y_mean) 
        P_xy /= N-1

        K = dot(P_xy, np.linalg.inv(P_yy))
        
        for j in range(N):
            thetas[j] += dot(K, p[i]+e_r[j]-y[j])
        theta=np.mean(thetas,axis=0)

        uxs.append(theta)
        uxs_std.append(np.std(thetas, axis=0))
        zs.append(y_mean)
        zs_std.append(np.std(y, axis=0))

    uxs=np.array(uxs)
    uxs_std=np.array(uxs_std)
    zs = np.array(zs).reshape(-1)
    zs_std = np.array(zs_std).reshape(-1)

    fig, ax = plt.subplots(2,2)
    ax[0,0].plot(t_multiple, p*1e-3, color='k')
    ax[0,0].plot(t_multiple,zs*1e-3, color='gray')
    ax[0,0].fill_between(t_multiple,
        (zs+zs_std)*1e-3,(zs-zs_std)*1e-3,color='gray', alpha=0.5)
    ax[0,0].set_ylim([60, 150])
    ax[0,0].set_ylabel('Pressure (mmHg)')
    ax[0,0].set_xlabel('t (s)')
    ax[0,1].plot(t_multiple, x_ini[0]*2**uxs[:,0], color='gray')
    ax[0,1].fill_between(t_multiple,
            x_ini[0]*2**(uxs[:,0]+uxs_std[:,0]),x_ini[0]*2**(uxs[:,0]-uxs_std[:,0]),
         color='gray', alpha=0.5)
    ax[0,1].plot(t_multiple, Rp*np.ones(len(p)), linestyle='--', color='k')
    ax[0,1].set_ylim([300, 5000])
    ax[0,1].set_ylabel('$R_p$ (dyne-s/$cm^5$)')
    ax[0,1].set_xlabel('t (s)')
    ax[1,0].plot(t_multiple, x_ini[1]*2**uxs[:,1], color= 'gray')
    ax[1,0].fill_between(t_multiple,
            x_ini[1]*2**(uxs[:,1]+uxs_std[:,1]),x_ini[1]*2**(uxs[:,1]-uxs_std[:,1]),
            color='gray', alpha=0.5)
    ax[1,0].plot(t_multiple, C*np.ones(len(p)), linestyle='--', color='k')
    ax[1,0].set_ylim([2e-6, 4e-5])
    ax[1,0].set_ylabel('C ($cm^5$/dyne)')
    ax[1,0].set_xlabel('t (s)')
    ax[1,1].plot(t_multiple, x_ini[2]*2**uxs[:,2], color='gray')
    ax[1,1].fill_between(t_multiple,
            x_ini[2]*2**(uxs[:,2]+uxs_std[:,2]),x_ini[2]*2**(uxs[:,2]-uxs_std[:,2]),
            color='gray', alpha=0.5)
    ax[1,1].plot(t_multiple, Rd*np.ones(len(p)), linestyle='--', color='k')
    ax[1,1].set_ylim([4000, 50000])
    ax[1,1].set_ylabel('$R_d$ (dyne-s/$cm^5$)')
    ax[1,1].set_xlabel('t (s)')
    plt.show()



