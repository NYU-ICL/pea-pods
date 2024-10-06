import imageio.v3 as iio
import numpy as np

from weibull import WeibullFn
import utils

class PEA:
    
    def __init__(
            self, 
            alpha_range=[0,1],
            color="black", 
            name=""
        ):
        """
        alpha_range: range of values to modulate PEA modality (alpha in manuscript)
        color: color for plotting
        name: name of PEA
        """
        
        self.alpha_range = alpha_range
        self.color = color 
        self.name = name
        
    def save_frame(self, img, alpha, **kwargs):
        img_modulated = utils.rgb2srgb(self.eval(img, alpha, **kwargs))
        iio.imwrite("output/frames/{}_{}.png".format(self.name, alpha), (255 * img_modulated).astype(np.uint8))
        return
        
    def get_Weibull(self):
        return WeibullFn("data/weibull_params/params_{}.csv".format("".join(self.name.split(" "))))

    def evaluate(self, img, save_name, alpha, **kwargs):
        """
        Apply a display mapping technique to an image
        
        -input img: input image in linear RGB space
        -input alpha: intensity of display mapping, higher is more distortion
        
        -output img with display mapping applied at alpha intensity
        """
        
        img_modulated = self.eval(img, alpha, **kwargs)
        
        if kwargs["save_frames"]:
            img_modulated_srgb = utils.rgb2srgb(img_modulated)
            iio.imwrite("output/frames/{}.png".format(save_name), (255 * img_modulated_srgb).astype(np.uint8))
            
        return img_modulated
        
    def eval(self, img, alpha, **kwargs):
        
        pass