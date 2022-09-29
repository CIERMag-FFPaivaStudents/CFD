#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Reads surface distance csv file and plot boxplot comparing multiple samples.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

def filter_dataFrame(df):
    """Filters a dataframe column within 3 standard deviation.

    Parameters
    ----------
    df: DataFrame
        Pandas data frame to be filtered.
    Returns
    -------
    filtered_df: DataFrame
        Filtered data frame.

    """

    z_scores = np.abs(stats.zscore(df))
    filtered_entries = (z_scores < 3).all(axis=1)
    filtered_df = df[filtered_entries]

    return filtered_df

if __name__=='__main__':

    file_list = ['/home/solcia/Documents/phd/CFDcases/3A/stlRecon/3A_distance.csv', 
                 '/home/solcia/Documents/phd/CFDcases/3B/stlRecon/3B_distance.csv',
                 '/home/solcia/Documents/phd/CFDcases/3C/stlRecon/3C_distance.csv']
    name_list = ['A', 'B', 'C']

    data_frame = pd.DataFrame()
    for (file_path,data_name) in zip(file_list,name_list):
        tmp_df = pd.read_csv(file_path, header=None, names=[data_name])
        filtered_df = filter_dataFrame(tmp_df) 
        data_frame = pd.concat([data_frame,filtered_df], axis=1)
  
    print("Median:")
    print(data_frame.median())
    
    sns.set_context('talk')
    sns.set_style('white')
    sns.catplot(data=data_frame, kind='violin',palette='Greys',
             aspect=4/3)
    plt.xlabel('Sample')
    plt.ylabel('Distance (mm)')
    plt.show()
