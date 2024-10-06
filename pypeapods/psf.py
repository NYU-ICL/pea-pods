import numpy as np
from scipy.optimize import minimize

def lorentzian(x, x0, I_offset, I0, FWHM_x):
    return I_offset + I0 * 1/(1+((x-x0)/(.5*FWHM_x)) ** 2)

def optimize_psf(df):
    mm, nits = df.mm, df.nits
    mm = mm - 19.106664226530896
    def psf(coef, x, y):
        x0, I_offset, I0, FWHM_x = coef[0], coef[1], coef[2], coef[3]
        return np.linalg.norm(y - lorentzian(x, x0, I_offset, I0, FWHM_x))
    
    res = minimize(psf, [0, 0, 36, 4], args=(mm, nits))
    x0, I_offset, I0, FWHM_x = res.x

    return x0, I_offset, I0, FWHM_x