#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Code to estimate the Grid Convergence Index as described in Procedure for Estimation and Reporting of Uncertainty Due to Discretization in CFD Applications [DOI: 10.1115/1.2960953].

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def computeRepresentativeCell(N, Volume):
    """

    """

    h = (Volume/N)**(1/3)

    return h

def computeRefinementFactor(N1, N2):
    """

    """

    r = (N2/N1)**(1/3)

    return r

def calculateApparentOrder(r_21, r_32, phi_1, phi_2, phi_3):
    """

    """
    tol =1e-12
    max_iter = 1000
    itr = 0
    error=1

    e_21 = phi_2 - phi_1
    e_32 = phi_3 - phi_2

    p = []
    for  e_32_i, e_21_i in zip(e_32, e_21):
    
        p_i = np.abs(np.log(np.abs(e_32_i/e_21_i)))/np.log(r_21)
    
        s = np.sign(e_32_i/e_21_i)

        while(error>tol and itr<max_iter):
            p0 = p_i
            q = np.log((r_21**p0-s)/(r_32**p0-s))

            p_i = np.abs(np.abs(np.log(np.abs(e_32_i/e_21_i)))+q)/np.log(r_21)

            error = np.linalg.norm(p_i-p0)
            itr +=1
        p.append(p_i)

    return p


if __name__=='__main__':

    #read number of cells (here I am assuming constant volume)
    sample='C'
    path = '/home/solcia/Documents/phd/CFDcases/3'+sample+'/data' 
    N_file = '/3'+sample+'_cells_data.csv'
    coarse_file = '/3'+sample+'_pressure_coarseSim.csv'
    fine_file = '/3'+sample+'_pressure_fineSim.csv'
    extraFine_file ='/3'+sample+'_pressure_extraFineSim.csv'
    experimental_file = '/3'+sample+'_pressure_experimental.csv'

    N_data = pd.read_csv(path+N_file, header=None)
    N1 = N_data[0].to_numpy()[0]
    N2 = N_data[1].to_numpy()[0]
    N3 = N_data[2].to_numpy()[0]
    

    coarse_data = pd.read_csv(path+coarse_file)
    fine_data = pd.read_csv(path+fine_file)
    extraFine_data = pd.read_csv(path+extraFine_file)
    experimental_data = pd.read_csv(path+experimental_file)
    
    phi_1 = coarse_data['pressure'].to_numpy()
    phi_2 = fine_data['pressure'].to_numpy()
    phi_3 = extraFine_data['pressure'].to_numpy()

    r_21 = computeRefinementFactor(N1, N2)
    r_32 = computeRefinementFactor(N2, N3)

    print(r_21)
    print(r_32)

    p = calculateApparentOrder(r_21, r_32, 
            phi_1, phi_2, phi_3)

    plt.figure()
    plt.plot(phi_1*997*1e-5, experimental_data['flow_rate'], label='coarse')
    plt.plot(phi_2*997*1e-5, experimental_data['flow_rate'], label='fine')
    plt.plot(phi_3*997*1e-5, experimental_data['flow_rate'], label='extrafine')
    plt.errorbar(experimental_data['pressure'], experimental_data['flow_rate'],
            xerr = 1e-3*np.ones(len(experimental_data['pressure'])),
            #yerr = experimental_data['flow_rate']*0.01,
            color='gray',marker='o', capsize=5, label='experimental')
    plt.legend()
    #plt.show()

    phi_21_extrapolated = (r_21**p*phi_1-phi_2)/(r_21**p-1)
    phi_32_extrapolated = (r_32**p*phi_2-phi_3)/(r_32**p-1)

    error_21 = np.abs((phi_1-phi_2)/phi_1)
    
    GCI_fine = 1.25*error_21/(r_21**np.mean(p)-1)
    #GCI_fine = 1.25*error_21/(r_21**p-1)
    
    plt.figure()
    plt.errorbar(fine_data['pressure']*997*1e-5, experimental_data['flow_rate'],
            xerr = GCI_fine*997*1e-5,marker='o', capsize=5, color = 'k', label='fine')
    plt.errorbar(experimental_data['pressure'], experimental_data['flow_rate'],
            xerr = 1e-3*np.ones(len(experimental_data['pressure'])),
            #yerr = experimental_data['flow_rate']*0.01, 
            color='gray',marker='o', capsize=5, label='experimental')
    #plt.xlim([0, 0.15])
    plt.legend()
    #plt.show()

    plt.figure(figsize=(6,6))
    sns.set()
    sns.set_context('talk')
    sns.set_style('ticks')
    plt.plot(experimental_data['flow_rate'],fine_data['pressure']*997*1e-5, 
            marker='o', color = 'k', label='simulation')
    plt.fill_between(experimental_data['flow_rate'], 
            fine_data['pressure']*997*1e-5-GCI_fine*997*1e-5,
            fine_data['pressure']*997*1e-5+GCI_fine*997*1e-5, color='k', alpha=0.2)
    plt.errorbar(experimental_data['flow_rate'],experimental_data['pressure'],
            color='gray',marker='o', label='experiment')
    plt.fill_between(experimental_data['flow_rate'],
            experimental_data['pressure']-1e-3*np.ones(len(experimental_data['pressure'])), 
            experimental_data['pressure']+1e-3*np.ones(len(experimental_data['pressure'])), 
            color='gray', alpha=0.2)
    plt.legend()
    plt.xlabel('flow rate (ml/min)')
    plt.ylabel('pressure (bar)')
    plt.savefig('/home/solcia/Documents/phd/PaperWormhole/Figs/pressure_curve'+sample+'.svg')
    plt.show()


