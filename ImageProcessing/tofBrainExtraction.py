#Author: Gustavo Solcia
#E-mail: gustavo.solcia@usp.br

"""Program to extract brain from Time of Flight (TOF) MRI using a T1 acquisition.
    Used brain extraction is the BET from FSL. RUN THIS CODE WITH fslpython!
    Saving outputs from FSL wrappers. LOOK AT YOUR DATA. Some steps could present errors.
"""

import nibabel as nib
import numpy as np
from fsl.data.image import Image
from fsl.wrappers import fslroi, robustfov, bet, LOAD
from fsl.wrappers.misc import fslreorient2std
from fsl.transform.affine import transform, concat
from fsl.utils.image.resample import resampleToReference

def transformTof2MaskCoord(tofVoxCoord, tofVox2World, maskWorld2Vox):
    
    floatCoord = transform(transform(tofVoxCoord,tofVox2World),
                            maskWorld2Vox).round()

    transfMaskVoxCoord = [int(item) for item in floatCoord]

    return transfMaskVoxCoord

def getTofMaskAffines(tof, mask):

    tofVox2World = tof.getAffine('voxel', 'world')
    maskWorld2Vox = mask.getAffine('world','voxel')

    return tofVox2World, maskWorld2Vox

def createBlankImage(baseImage):

    data = np.zeros(baseImage.shape)

    blankImage = Image(data, header=baseImage.header)

    return blankImage

def isInsideMaskSpace(transfMaskVoxCoord, maskShape):
    boolean = (transfMaskVoxCoord[0]>=0 and transfMaskVoxCoord[0]<maskShape[0]) and \
                        (transfMaskVoxCoord[1]>=0 and transfMaskVoxCoord[1]<maskShape[1]) and\
                        (transfMaskVoxCoord[2]>=0 and transfMaskVoxCoord[2]<maskShape[2])
    return boolean

def convertMask2Tof(tof, mask):

    tofShape = tof.shape
    maskShape = mask.shape

    tofMask = createBlankImage(tof)

    tofVox2World, maskWorld2Vox = getTofMaskAffines(tof, mask)
    
    for i in range(tofShape[0]): #This can take a LONG time
        for j in range(tofShape[1]): #Clearly three for's is not the best solution
            for k in range(tofShape[2]): #feel free to contribute with a better solution!
                
                tofVoxCoord = [i, j, k]
                transfMaskVoxCoord = transformTof2MaskCoord(tofVoxCoord, tofVox2World, maskWorld2Vox)

                if(isInsideMaskSpace(transfMaskVoxCoord, maskShape)):
                    tofMask.data[i,j,k] = mask.data[transfMaskVoxCoord[0],transfMaskVoxCoord[1],
                                                    transfMaskVoxCoord[2]]

    return tofMask

if __name__=='__main__':

    inputT1 = 'IXI362-HH-2051-T1'
    inputTOF = 'IXI362-HH-2051-MRA'

    fslreorient2std(inputT1, inputT1+'_reorient')
    fslreorient2std(inputTOF, inputTOF+'_reorient')

    robustfov(inputT1+'_reorient',inputT1+'_robust')
    
    bet(inputT1+'_robust', inputT1+'_brain', R=True, m = True) 

    mask = Image(inputT1+'_brain_mask')
    tof = Image(inputTOF+'_reorient')
    
    tofMask = convertMask2Tof(tof, mask)

    tofMask.save(inputTOF+"_brain_mask")

