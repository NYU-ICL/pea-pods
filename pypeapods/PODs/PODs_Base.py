
class POD:
    
    def __init__(
            self, 
            measurements_pth="",
            name=""
        ):
        self.measurements_pth = measurements_pth
        self.name = name
        
    def fit_model(self):
        pass

    def evaluate(self, img, **kwargs):
        """
        Compute static and dynamic power consumption when displaying img
        
        -input img: input image in linear RGB space
        
        -output static/dynamic power consumption in mW
        """
        pass