import sys

# Color foveation model path
sys.path.append('../third_party/vr-power-saver')
from color_model.base_color_model import BaseColorModel
from util.colorspace import RGB2XYZ, XYZ2RGB

import numpy as np

from PEA.PEA_Base import PEA
import utils

class WhitepointShift(PEA):
    
    def __init__(self, alpha_range=[0,1], color="black", name=""):
        super().__init__(alpha_range, color, name)
        
        # Load Model
        self.model = BaseColorModel()
        self.model.initialize()
        self.model.load("../third_party/vr-power-saver/io/color_model/model.pth")
        
        # Power model vector
        energy_vec = [231.5384684, 245.6795914, 530.7596369, 977.2813229]
        self.energy_vec = -np.array(energy_vec[:-1])
        
    def compute_CAT(self, wp, wp_new):
        M_A = np.array([[0.8951000,  0.2664000, -0.1614000],
                        [-0.7502000,  1.7135000,  0.0367000],
                        [0.0389000, -0.0685000,  1.0296000]])
        M_A_inv = np.array([[0.9869929, -0.1470543,  0.1599627],
                        [0.4323053,  0.5183603,  0.0492912],
                        [-0.0085287,  0.0400428,  0.9684867]])

        scale_S = M_A @ wp
        scale_D = M_A @ wp_new
        S = np.array([[scale_D[0]/scale_S[0],0,0],[0,scale_D[1]/scale_S[1],0],[0,0,scale_D[2]/scale_D[2]]])
        return M_A_inv @ S @ M_A

    def eval(self, img, alpha, **kwargs):
        avg_pixel_color = np.mean(utils.rgb2srgb(img), axis=(0, 1)).reshape(1, 3)
        out = self.model.apply_filter(avg_pixel_color, np.zeros((1, 1)), self.energy_vec)

        d65 = np.array([95.04, 100, 108.88]) / 100 # XYZ D65
        vec = out - avg_pixel_color
        wp = RGB2XYZ @ utils.srgb2rgb(utils.rgb2srgb(XYZ2RGB @ d65) + vec[0] * alpha)
        M = self.compute_CAT(d65, wp)
        shifted = (XYZ2RGB @ M @ RGB2XYZ @ img.reshape(-1,3).T).T
        out = shifted.reshape(img.shape)
        return out