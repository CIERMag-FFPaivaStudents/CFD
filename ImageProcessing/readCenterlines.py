#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Import a polydata centerline file (VMTK output) and prints mean radius and lenght per branch. Make sure that the ID is not related with a junction (you can check using Paraview).

"""

import vtk
import numpy as np
import matplotlib.pyplot as plt
from vtk.util.numpy_support import vtk_to_numpy

def read_data(input_file):
    """Read centerline .vtp data and returns radius, identification, and paths for each centerline branch.

    Parameters
    ----------
    input_file: str
        Centerline .vtp (polydata) file.

    Returns
    -------
    radius: array
        Radius from maximum inscribed spheres from centerlines paths.
    ID: array
        ID for each centerline branch. Attention: it can include junctions! Look at your data to only consider branch values.
    path: array
        Path lenght for each branch. 

    """

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(input_file)
    reader.Update()

    polydata = reader.GetOutput()

    radius = vtk_to_numpy(polydata.GetPointData().GetArray('MaximumInscribedSphereRadius'))
    ID = vtk_to_numpy(polydata.GetPointData().GetArray('BranchId'))
    path = vtk_to_numpy(polydata.GetPointData().GetArray('Path'))

    return radius, ID, path

if __name__=='__main__':

    input_file = 'centerlines.vtp'

    radius, ID, path = read_data(input_file)

    plt.figure()
    for unique_val in np.unique(ID):
        print('mean radius (ID '+str(unique_val)+'):'+str(np.mean(radius[ID==unique_val])))
        print('len (ID '+str(unique_val)+'):'+str(np.max(path[ID==unique_val])))
        plt.hist(radius[ID==unique_val], label=str(unique_val))
    plt.legend()
    plt.xlabel('Radius (mm)') # Usually in mm! Check your data
    plt.ylabel('Frequency')
    plt.show()

