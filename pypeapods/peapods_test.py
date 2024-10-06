import numpy as np
from glob import glob

# PEA
from PEA.PEA_uniformdimming import UniformDimming
from PEA.PEA_luminanceclipping import LuminanceClipping
from PEA.PEA_brightnessrolloff import BrightnessRolloff
from PEA.PEA_dichopticdimming import DichopticDimming
from PEA.PEA_colorfoveation import ColorFoveation
from PEA.PEA_whitepointshift import WhitepointShift

# PODs
from PODs.PODs_globalLC import GlobalLC
from PODs.PODs_localLC import LocalLC
from PODs.PODs_oled import OLED

from peapods import PEAPODs

if __name__ == "__main__":
    
    # Initialize power models
    globalLC = GlobalLC(measurements_pth="data/mqp_display/mqp_BLU.csv", name="Global Dimming LC")
    localLC = LocalLC(measurements_pth="data/mqp_display/mqp_BLU.csv", name="Local Dimming LC")
    oled = OLED(name="OLED")
    pods = [oled, globalLC, localLC]
    
    # Initialize display mapping techniques
    uniformdimming = UniformDimming(color="limegreen", name="Uniform Dimming")
    luminanceclipping = LuminanceClipping(color="darkviolet", name="Luminance Clipping")
    brightnessrolloff = BrightnessRolloff(color="gold", name="Brightness Rolloff")
    dichopticdimming = DichopticDimming(color="violet", name="Dichoptic Dimming")
    whitepointshift = WhitepointShift(alpha_range=[0,5.2], color="cornflowerblue", name="Whitepoint Shift")
    colorfoveation = ColorFoveation(color="tomato", name="Color Foveation")
    pea = [whitepointshift, uniformdimming, luminanceclipping, dichopticdimming, brightnessrolloff, colorfoveation]
    
    # read image resolution
    img_pths = glob("data/study_imgs/*.png") # list of image paths
    
    # compute eccentricity map
    H, W = 1800, 1920
    xv, yv = np.meshgrid(np.linspace(0, W, W), np.linspace(0, H, H))
    dist = ((xv - W/2) ** 2 + (yv - H/2) ** 2) ** .5
    
    display_params = {
        "ppd": 22,
        "foveal_region": 10,
        "FOV": 110,
        "distance": dist,
        "save_frames": True,
        "resolution": [H, W]
    }
    
    # Create PEAPODs object
    N_alpha = 3 # number of points to sample along Weibull transfer function
    pp = PEAPODs(PEA=pea, PODs=pods, img_pths=img_pths, display_params=display_params, N_alpha=N_alpha)
    
    # Plot transfer curves
    ret_d = pp.plot_jod2mw()
    np.save("output/ret_d.npy", ret_d)