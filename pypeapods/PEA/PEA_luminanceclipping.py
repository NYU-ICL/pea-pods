import numpy as np

from PEA.PEA_Base import PEA
import utils

class LuminanceClipping(PEA):
    
    def __init__(self, alpha_range=[0,1], color="black", name=""):
        super().__init__(alpha_range, color, name)

    def eval(self, img, alpha, **kwargs):
        lum = utils.y(img)
        idx = lum > (1-alpha)
        img_copy = img.copy()
        img_copy[idx] = img_copy[idx] * ((1-alpha)/lum[idx, np.newaxis])
        return img_copy