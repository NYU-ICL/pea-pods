from PODs.PODs_Base import POD
import numpy as np

class OLED(POD):
    
    def __init__(
            self, 
            measurements_pth="",
            name=""
        ):
        
        super().__init__(measurements_pth, name)

    def evaluate(self, img, **kwargs):
        energy_vec = [231.5384684, 245.6795914, 530.7596369, 977.2813229]
        H, W = img.shape[:2]
        r = np.sum(img[...,0] * energy_vec[0]) / (H*W)
        g = np.sum(img[...,1] * energy_vec[1]) / (H*W)
        b = np.sum(img[...,2] * energy_vec[2]) / (H*W)
        w = energy_vec[3]
        dynamic_power = r + g + b
        total_power = dynamic_power + w
        return total_power, dynamic_power
