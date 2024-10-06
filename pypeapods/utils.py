import numpy as np
from scipy.stats import norm

def p_pref_to_jod(p_pref):
    """
    See https://github.com/gfxdisp/FovVideoVDP for reference implementation.
    """
    sigma_cdf = 1.4826; # The standard deviation for the JOD/JND units (1 JOD = 0.75 p_A_better)
    return norm.ppf(((2*p_pref-1) * 100 + 100)/2 * 1/100, 0, sigma_cdf)

def jod_to_p_pref(jods):
    sigma_cdf = 1.4826; # The standard deviation for the JOD/JND units (1 JOD = 0.75 p_A_better)
    p_A_better = norm.cdf( jods, 0, sigma_cdf ) * 100
    p_pref = (p_A_better*2-100)/100
    return (p_pref+1)*.5

def srgb2rgb(srgb):
    srgb = np.clip(srgb, 0.0, 1.0)
    return np.where(srgb > 0.04045, ((srgb + 0.055) / 1.055) ** 2.4, srgb / 12.92)

def rgb2srgb(rgb):
    rgb = np.clip(rgb, 0.0, 1.0)
    return np.where(rgb > 0.0031308, (1.055 * (rgb ** (1 / 2.4))) - 0.055, 12.92 * rgb)

def y(img):
    """
    Linear RGB to relative luminance
    """
    return img[...,0] * .2126 + img[...,1] * .7152 + img[...,2] * .0722