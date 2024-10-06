from PODs.PODs_Base import POD
import numpy as np
import pandas as pd

class GlobalLC(POD):
    
    def __init__(
            self, 
            measurements_pth="",
            name=""
        ):
        
        super().__init__(measurements_pth, name)
        self.fit_model()
        
    def fit_model(self):
        df = pd.read_csv(self.measurements_pth)
        m, b = np.polyfit(df['x'], df['y'], 1)
        self.params = [m, b]

    def evaluate(self, img, **kwargs):
        dynamic_power = img.max() * self.params[0]
        total_power = dynamic_power + self.params[1]
        return total_power, dynamic_power