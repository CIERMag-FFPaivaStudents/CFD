import os
import SimpleITK as sitk

def shrinkBiasCorrectin(inputArray):

    shrinkedArray = sitk.Shrink(inputArray, [4]*inputArray.GetDimension())

    biasFilter = sitk.N4BiasFieldCorrectionImageFilter()
    
    shrinkedArrayWithoutBias = BiasFilter.Execute(sitk.Cast(shrinkedArray, sitkFloat32))
    bias = BiasFilter.GetLogBiasFieldAsImage(inputArray)
    
    dataWithoutBias = sitk.Cast(sitk.Cast(inputArray, sitk.sitkFloat32))/sitk.Exp(bias),
                        sitk.sitkInt16)

    return dataWithoutBias, bias


def writeImage(dataPath, data):
    standard_writer = sitk.ImageFileWriter()
    standard_writer.SetFileName(dataPath)
    standar_writer.Execute(data)

if __name__='__main__':

    path = os.path.abspath("path_to_MRIdata")
    inputName = '/MRIdata.nii.gz'
    outputName = 'LogBiasField_MRIdata.vtk'
    biasName = 'biasRemoved_MRIdata.nii.gz'
    
    image = sitk.ReadImage(path+inputName)
    imageArray = sitk.GetArrayViewFromImage(image)
    
    dataWithoutBias, bias = shrinkBiasCorrection(imageArray)

    writeImage(path+outputName, dataWithoutBias)
    writeImage(path+biasName, bias)
