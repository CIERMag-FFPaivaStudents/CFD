# Author: Gustavo Solcia
# E-mail: gustavo.solcia@usp.br

"""Denoising using a modified Non-Local Means for Rician noise.

"""

import sys

sys.path.append('../../NLM') #ATENTION: This path depends on where you cloned our NLM repository

import os
import SimpleITK as sitk
from modifiedNLM.estimate.noise_estimate import rician_estimate
from modifiedNLM.filter.modified_nl_means import rician_denoise_nl_means


def NLM(imageData):

    """Wrapper of modified NLM imported from https://github.com/CIERMag-FFPaivaStudents/NLM.

    Parameters
    ----------
    imageData: array
        Numpy array from image desired to denoise. Atention: Be shure your image has Rician noise.

    Returns
    -------
    denoisedData: array
        Denoised array from rician_denoise_nl_means.

    """

    ricianSigma = rician_estimate(imageData)
    patch_kw = dict(patch_size=5,      # 5x5 patches
                patch_distance=6,  # 13x13 search area
                multichannel=False,
                preserve_range=True)
    denoisedData = rician_denoise_nl_means(imageData, h=1.15 * ricianSigma, fast_mode=False,
                           **patch_kw)
    return denoisedData

def createSITKcopy(image, array):

    """Create new sitk image from array with same information from base image.

    Parameters
    ----------

    Returns
    -------

    """
    
    copy = sitk.GetImageFromArray(array)
    copy.CopyInformation(image)

    return copy


if __name__ == '__main__':

    path = os.path.abspath('/home/solcia/Documents/phd/MRI data/rocks/3C/PSIF300/')
    name = '/standard_s4_3C.nii.gz'
    image = sitk.ReadImage(path+name)
    imageData = sitk.GetArrayViewFromImage(image)

    denoisedData = NLM(imageData)

    denoised = createSITKcopy(image, denoisedData)

    standard_writer = sitk.ImageFileWriter()
    standard_writer.SetFileName(path+'denoised_3C.nii.gz')
    standard_writer.Execute(denoised)
