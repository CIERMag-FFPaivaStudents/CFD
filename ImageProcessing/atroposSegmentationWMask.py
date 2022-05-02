# Author: Gustavo Solcia
# E-mail: gustavo.solcia@usp.br

"""Wrapper of atropos segmentation from advanced normalization tools (ANTs).
   This code considers you have a mask to help the segmentation process.

"""
import os 
import ants
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

def convertSitkToAnts(sitkImage):

    """Conversor of sitkImage to antsImage.

    Parameters
    -----------
    sitkImage: sitkImage
        Image desired to convert.


    Returns
    --------
    antsImage: antsImage
        Converted image.


    """

    array = sitk.GetArrayFromImage(sitkImage)
    antsImage = ants.from_numpy(array.astype('float32'))

    return antsImage

def getSegmentationArray(antsImage, antsMask):
    
    """Atropos segmentation from Advanced Normalization Tools returned as a numpy array.

    Parameters
    ----------
    antsImage: antsImage
        Image you want to apply segmentation.
    antsMask: antsImage
        Mask used on atropos segmentation.

    Returns
    -------
    segmentationArray: array
        Segmented image on array with corrected axis.

    """

    segmentationAnts = ants.atropos(a=antsImage, m='[0.5, 1x1x1]', c='[50, 0.0001]',
                                i='kmeans[3]', p='Socrates[1]', x=antsMask)

    segmentationArray = segmentationAnts['segmentation'].numpy()

    return segmentationArray

def writeArrayImage(dataPath, sitkImage, array):

    """Image writing operation with array conversion.

    Parameters
    ----------
    dataPath: string
        String containing a path to the directory + the data name.
    sitkImage: sitkImage
        sitkImage (usually the input) that we use to copy information.
    array: array
        Numpy array you want to save.


    """

    newSitkImage = sitk.GetImageFromArray(array)
    newSitkImage.CopyInformation(sitkImage)

    standard_writer = sitk.ImageFileWriter()
    standard_writer.SetFileName(dataPath)
    standard_writer.Execute(newSitkImage)



if __name__ == '__main__':

    path = os.path.abspath("datapath") #insert your data path here

    inputName = '/IXI132-HH-1415-MRA_brain.nii.gz'
    outputName = '/IXI132-HH-1415-MRA_brain_seg.nii.gz' #The forward slash is necessary to path+*Name work!
    maskName = '/IXI132-HH-1415-MRA_brain_mask.nii.gz'

    sitkImage = sitk.ReadImage(path+inputName)
    sitkMask = sitk.ReadImage(path+maskName)

    antsMask = convertSitkToAnts(sitkMask)
    antsImage = convertSitkToAnts(sitkImage)

    segmentationArray = getSegmentationArray(antsImage, antsMask)

    writeArrayImage(path+outputName, sitkImage, segmentationArray)

    
