from PODs.PODs_Base import POD
import numpy as np
import pandas as pd

from skimage.transform import resize
import psf

class LocalLC(POD):
    
    def __init__(
            self, 
            measurements_pth="",
            name=""
        ):
        
        super().__init__(measurements_pth, name)
        self.fit_model()
        
        self.v = 750
        df = pd.read_csv("data/mqp_display/mqp_PSF.csv")
        x0, I_offset, I0, FWHM_x = psf.optimize_psf(df)
        self.PSF = lambda x : psf.lorentzian(x, x0, I_offset, I0, FWHM_x)
        
    def fit_model(self):
        df = pd.read_csv(self.measurements_pth)
        m, b = np.polyfit(df['x'], df['y'], 1)
        self.params = [m, b]

    def evaluate(self, img, **kwargs):
        blu = np.zeros(img.shape)
    
        # set as max of all intensities
        ny, nx = 32, 18
        
        # num LEDs per row
        num_per_row = np.array([10, 10, 12, 12, 14, 16, 16, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 16, 16, 14, 12, 12, 10, 10])
        num_per_row = num_per_row.astype(np.uint8)
        w_dist, h_dist = 2.2222, 1.25
        
        blu = resize(np.max(img * self.v, axis=2), (ny, nx))
        blu_flat = np.zeros(np.sum(num_per_row))
        start = 0
        for i in range(len(num_per_row)):
            num = num_per_row[i]
            start_i = int((nx - num)/2)
            blu_flat[start:start+num] = blu[i, start_i:start_i+num]
            start = start+num
            
        # Derive LED intensities
        start_i, k, d_out = 0, 0, np.zeros(np.sum(num_per_row))
        for r in range(len(num_per_row)):
            num_leds = num_per_row[r]
            for c in range(nx):
                nh, bs, start_i = 2, [], int((nx - num_leds)/2)
                if c < start_i or c > num_leds + start_i-1:
                    continue
                # compute neighborhood around LED
                for c_ in np.arange(c - nh, c + nh):
                    for r_ in np.arange(r - nh, r + nh):
                        if r_ < 0 or c_ < 0 or r_ > ny-1 or c_ > nx-1:
                            continue 
                        if c_ == c and r_ == r:
                            continue
                        if c_ < start_i or c_ > num_leds + start_i-1:
                            continue
                        # distance between neighbor and LED
                        dist = np.linalg.norm(np.asarray([r_*h_dist,c_*w_dist]) - np.asarray([r*h_dist,c*w_dist]))
                        # compute PSF at dist
                        bs += [self.PSF(dist) * blu[r_, c_]/self.v]
                if len(bs) == 0:
                    bs = [0]
                d_out[k] = np.clip((blu[r,c] - np.sum(bs)) / self.v, 0, 1)
                k += 1

        N_zones = np.sum(num_per_row)
        d_out = d_out.reshape(-1)
        
        # compute power
        static_power = np.sum(d_out * self.params[0]) / N_zones + self.params[1]
        dynamic_power = np.sum(d_out * self.params[0]) / N_zones
        return static_power, dynamic_power