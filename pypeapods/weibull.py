import numpy as np
import pandas as pd

# see https://psychopy.org/api/data.html#psychopy.data.FitWeibull
class WeibullFn:
    
    def __init__(self, param_pth, chance=0.5):
        self.param_pth = param_pth
        self.chance = chance
        self.load_params()
        
    def load_params(self):
        df = pd.read_csv(self.param_pth)
        self.a =  df.loc[0].at["a"]
        self.b =  df.loc[0].at["b"]
    
    def eval(self, x):
        return self.chance + (1.0 - self.chance) * (1 - np.exp(-(x / self.a) ** self.b))
    
    def inv(self, y):
        return self.a * (-np.log((1.0-y) / (1-self.chance))) ** (1.0/self.b)