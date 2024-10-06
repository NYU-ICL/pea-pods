import os
import imageio.v3 as iio
import numpy as np

import utils
from PEA.PEA_uniformdimming import UniformDimming
from PODs.PODs_globalLC import GlobalLC

os.makedirs('output/frames', exist_ok=True)

# load an image
pth = "data/study_imgs/Sculpture1.png"
image = utils.srgb2rgb(iio.imread(pth)/255)

# define PEA and POD
globalLC = GlobalLC(measurements_pth="data/mqp_display/mqp_BLU.csv", name="Global Dimming LC")
uniformdimming = UniformDimming(color="limegreen", name="Uniform Dimming")

# compute eccentricity map
H, W = 1800, 1920
xv, yv = np.meshgrid(np.linspace(0, W, W), np.linspace(0, H, H))
dist = ((xv - W/2) ** 2 + (yv - H/2) ** 2) ** .5

# define display parameters
display_params = {
    "ppd": 22,
    "foveal_region": 10,
    "FOV": 110,
    "distance": dist,
    "save_frames": True,
    "resolution": [H, W]
}

# apply PEA modality (uniform dimming by alpha=50%)
alpha = 0.5
image_modulated = uniformdimming.evaluate(image, "globalLC_uniformDimming", alpha, **display_params)

# compute dynamic power consumption for modulated and reference image
_, power_modulated = globalLC.evaluate(image_modulated)
_, power_reference = globalLC.evaluate(image)

# compute savings
savings = (1 - power_modulated / power_reference) * 100 

# should print 50
print(str(savings) + "% savings")