from PEA.PEA_Base import PEA

class UniformDimming(PEA):
    
    def __init__(self, alpha_range=[0,1], color="black", name=""):
        super().__init__(alpha_range, color, name)

    def eval(self, img, alpha, **kwargs):
        return (1 - alpha) * img