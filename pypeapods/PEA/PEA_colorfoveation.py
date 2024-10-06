import sys

# Color foveation model path
sys.path.append('../third_party/vr-power-saver')
from color_model.base_color_model import BaseColorModel

import numpy as np

from PEA.PEA_Base import PEA
import utils

class ColorFoveation(PEA):
    
    def __init__(self, alpha_range=[0,1], color="black", name=""):
        super().__init__(alpha_range, color, name)
        
        # Load Model
        self.model = BaseColorModel()
        self.model.initialize()
        self.model.load("../third_party/vr-power-saver/io/color_model/model.pth")
        
        # Power model params [Duinkharjav & Chen et. al, SIGGRAPH Asia 2022]
        energy_vec = [231.5384684, 245.6795914, 530.7596369, 977.2813229]
        self.energy_vec = -np.array(energy_vec[:-1])

    def eval(self, img, alpha, **kwargs):
        ecc = kwargs['distance'] / kwargs['ppd']
        idx = ecc < kwargs['foveal_region']
        end_lerp = 15

        img_copy = utils.rgb2srgb(img.copy())
        out_img = self.model.apply_filter(img_copy, ecc, self.energy_vec)
        out_img[idx] = img_copy[idx]
        ecc = ecc[:,:,np.newaxis]
        alpha = alpha * np.clip((ecc-10)/end_lerp, 0, 1)
        out_img = ((1-alpha) * img_copy + alpha * out_img)
        return utils.srgb2rgb(out_img)