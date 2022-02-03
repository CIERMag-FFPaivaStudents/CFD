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

if __name__=='__main__':

    inputT1 = 'IXI362-HH-2051-T1'
    inputTOF = 'IXI362-HH-2051-MRA'

    fslreorient2std(inputT1, inputT1+'_reorient')
    fslreorient2std(inputTOF, inputTOF+'_reorient')

    robustfov(inputT1+'_reorient',inputT1+'_robust')
    
    bet(inputT1+'_robust', inputT1+'_brain', R=True, m = True) 

    mask = Image(inputT1+'_brain_mask')
    tof = Image(inputTOF+'_reorient')

    tofVox2World = tof.getAffine('voxel', 'world')
    maskWorld2Vox = mask.getAffine('world','voxel')

    print(mask.sameSpace(tof))
    print(maskVox2World)
    print(tofWorld2Vox)
    
    mask2tof = concat(maskVox2World,tofWorld2Vox)
    tof2mask = concat(tofVox2World,maskWorld2Vox)

    print(transform(transform([255,255,0],tofVox2World),maskWorld2Vox).round())

    
    #I'm still working on this transformation
    fslroi(inputT1+'_brain_mask', inputT1+'_brain_mask_roi',
