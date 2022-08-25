#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Code usefull for plotting post-processing scalar values. If you want to just visualize your data, I would recommend just using foamMonitor. 
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_data(file_name,data_type):
    """Reads post processing data depending on the type of scalar values

    Parameters
    ----------
    file_name: str
        data file path.
    data_type: str
        data type (surfaceScalarField or scalarProbe).

    Returns
    -------
    t: array
        time array from simulation file.
    data: array
        post-processing data.
    """

    if (data_type=='surfaceScalarField'):
        dataframe = pd.read_csv(file_name, sep='\t', header=4)
    elif (data_type=='scalarProbe'):
        dataframe = pd.read_csv(file_name, sep='\s+', header=2)
    
    t = dataframe.iloc[:,0].to_numpy()
    data = dataframe.iloc[:,1].to_numpy()

    return t, data

if __name__=='__main__':

    post_processing_file = '/home/solcia/Documents/phd/CFDcases/RightCarotid_stenosis/postProcessing/probe_EC/0'
    data_file = '/p'

    data_type = 'scalarProbe'
    data_name = 'pressure'

    t, data = read_data(post_processing_file+data_file, data_type)

    plt.figure(figsize=(10,8))
    sns.set()
    sns.set_context('talk')
    sns.set_style('white')
    plt.plot(t,data, color='k')
    plt.xlabel('t (s)')
    plt.ylabel(data_name)
    plt.show()

