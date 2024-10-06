import numpy as np

from PEA.PEA_Base import PEA

class BrightnessRolloff(PEA):
    
    def __init__(self, alpha_range=[0,1], color="black", name=""):
        super().__init__(alpha_range, color, name)

    def eval(self, img, alpha, **kwargs):
        ecc = kwargs['distance'] / kwargs['ppd']
        ecc_rad = np.deg2rad(ecc-kwargs['foveal_region'])
        FOV = np.deg2rad(kwargs['FOV']-kwargs['foveal_region'])
        eps = 1e-7
        beta = -4 * np.log(1 - alpha + eps) / (FOV * FOV)
        lum = np.exp(-beta * ecc_rad ** 2)
        idx = ecc < kwargs['foveal_region']
        lum[idx] = 1
        return img * lum[:,:,np.newaxis]