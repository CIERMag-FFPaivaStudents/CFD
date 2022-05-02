# Author: Gustavo Solcia
# E-mail: gustavo.solcia@usp.br

"""3D reconstruction using a segmentation image. We apply Marching Cubes algorithm and a 
   surface smoothing from the largest connected region. LOOK AT YOUR DATA: for some cases 
   the surface smoothing can shrink parts of your surface.
"""

import os
import vtk
import SimpleITK as sitk

def applyMarchingCubes(image, threshold):

    """Wrapper function to apply vtk marching cubes algorithm.

    Parameters
    ----------
    image: vtkImage
        vtkImage from vtkNIFTIImageReader
    threshold: float
        threshold for binarization purposes

    Returns
    -------
    largestRegion: vtkPolyData
        vtk data object that represents a geometric structure with vertices, lines, polygons...

    """
    contourNumber = 0

    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputData(image)
    marchingCubes.ComputeNormalsOn()
    marchingCubes.ComputeGradientsOn()
    marchingCubes.SetValue(contourNumber, threshold)
    marchingCubes.Update()

    mcPoly = marchingCubes.GetOutput()

    largestRegion = getLargestRegion(mcPoly)

    return largestRegion


def getLargestRegion(poly):

    """Function to get largest connected region from vtk poly data.

    Parameters
    ----------
    poly: vtkPolyData
        vtk data object that represents a geometric structure with vertices, lines, polygons...

    Returns
    -------
    largestRegion: vtkPolyData
        largest connected region from poly input

    """
    
    connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
    connectivityFilter.SetInputData(poly)
    connectivityFilter.SetExtractionModeToLargestRegion()
    connectivityFilter.Update()

    largestRegion = connectivityFilter.GetOutput()
    
    return largestRegion

def applyPolyFilter(poly):

    """Function that apply a surface vtk poly data filter. 

    Parameters
    ----------
    poly: vtkPolyData
        vtk data object that represents a geometric structure with vertices, lines, polygons...

    Returns
    -------
    smoothPoly: vtkPolyData
        smooth surface from poly input

    """

    #These are parameters that worked fine for most of my applications.
    #However, if you are having shrinking problems: 
    #-First, I would consider a higher passBand (e. g., 0.3, 0.4, 0.5, etc...).
    #-Second, with a different passBand, I would increase the numberOfIterations
    #and gradually decrease that number (but never going less than 100 iterations).
    numberOfIterations = 100
    passBand = 0.25
    featureAngle = 120.0
    
    polyFilter = vtk.vtkWindowedSincPolyDataFilter()
    polyFilter.SetInputData(poly)
    polyFilter.SetNumberOfIterations(numberOfIterations)
    polyFilter.SetPassBand(passBand)
    polyFilter.SetFeatureAngle(featureAngle)
    polyFilter.Update()

    smoothPoly = polyFilter.GetOutput()
    return smoothPoly

def readImage(path, name):

    """vtkNIFTI image reader wrapper function.

    Parameters
    ----------
    path: string
        String containing a path to the data directory
    name: string
        String containing the data or sample name

    Returns
    -------
    image: vtkNIFTIImage
        Desired image from path+name

    """
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(path+name)
    reader.Update()

    image = reader.GetOutput()

    return image

def writeSTL(path, name, poly):

    """STL writting function for vtkPolyData.

    Parameters
    ----------
    path: string
        String containing a path to the data directory
    name: string
        String containing the data or sample name
    poly: vtkPolyData
        vtk data object that represents a geometric structure with vertices, lines, polygons...

    """

    writer = vtk.vtkSTLWriter()
    writer.SetInputData(poly)
    writer.SetFileName(path+name)
    writer.Update()

if __name__=='__main__':
    
    sample = '3C'
    inputPath = os.path.abspath('/home/solcia/Documents/phd/MRI data/rocks/'+sample+'/PSIF300/')
    outputPath = os.path.abspath('/home/solcia/Documents/phd/3DModels/rocks/'+sample+'/')
    inputName = '/Atropos_'+sample+'.nii.gz'
    cubesOutputName = '/cubes_'+sample+'.stl'
    smoothOutputName = '/smooth_'+sample+'.stl'

    threshold = 2.5

    vtkImage = readImage(inputPath, inputName)

    mcPoly = applyMarchingCubes(vtkImage, threshold)

    polyFiltered = applyPolyFilter(mcPoly)

    writeSTL(outputPath,cubesOutputName, mcPoly)

    writeSTL(outputPath,smoothOutputName, polyFiltered)
