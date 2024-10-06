import numpy as np
from scipy import stats
import imageio.v3 as iio
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
from skimage.transform import resize

import os

import utils

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif"
})

class PEAPODs:
    
    def __init__(self, PEA, PODs, img_pths, N_alpha=40, save_pth="output", display_params=[]):
        """
        PEA: list of display mappings overloading the PEA_Base class
        PODs: list of display power models overloading the POD_Base class
        img_pths: list of image paths to run power/display mapping techniques on
        N_alpha: number of samples along psychometric function
        """
        self.PEA = PEA
        self.PODs = PODs
        self.img_pths = img_pths
        self.N_alpha = N_alpha
        self.display_params = display_params
        
        self.save_pth = save_pth
        
        # Load images
        self.imgs = [resize(utils.srgb2rgb(iio.imread(pth)/255), display_params["resolution"]) for pth in self.img_pths]
        
        # Load study results
        self.study_results = pd.read_csv('data/study_results/pwcmp_JOD.csv')
        row_temp = self.study_results.loc[self.study_results['condition'] == 'Reference_0'].to_numpy()[0]
        self.ref_jod = row_temp[1]
        ref_jod_se = row_temp[2]
        
        # plot reference line
        plt.axvline(0, color="black", linestyle="--")
        plt.errorbar(0, 25, xerr=ref_jod_se, color="black", capsize=3)
        
        # Compute reference powers
        self.ref_powers = {}
        for pod in self.PODs:
            self.ref_powers[pod.name] = np.asarray([pod.evaluate(img)[1] for img in self.imgs])
            
        # Create empty directory for figs
        os.makedirs(self.save_pth, exist_ok=True)
        
    def plot_measurements(self, pea, pod, pbar):
        for level in [0, 1, 2]:
            peaLevel = pea.name.replace(' ', '') + '_{}'.format(level)
            _, jod, jod_se, alpha = self.study_results.loc[self.study_results['condition'] == peaLevel].to_numpy()[0]
            
            dynamic_powers = []
            pod_arr = []
            i = 0
            for img in self.imgs:
                img_name = self.img_pths[i].split("/")[-1].split(".")[0].replace(" ", "_")
                save_name = "{}_{}_{}_{}".format(img_name, pea.name.replace(" ", "_"), pod.name, 'MEAS')
                pod_arr += [pod.evaluate(pea.evaluate(img, save_name, alpha, **self.display_params))[1]]
                pbar.update(1)
                i += 1
            
            dynamic_powers += [np.asarray(pod_arr)]
            savings = [(1 - power / self.ref_powers[pod.name]) * 100 for power in dynamic_powers]
                        
            mean_powers = np.mean(savings)
            sem_powers = stats.sem(savings, axis=None)
            
            if pea.name == "Dichoptic Dimming":
                mean_powers *= 0.5
            
            plt.errorbar([jod-self.ref_jod], [mean_powers], xerr=[jod_se], yerr=[sem_powers], capsize=3, color=pea.color, marker='o', markersize=3)
    
    def plot_jod2mw(self):
        ret_d = {}
        min_JOD = -3.4
        jods = np.linspace(0, min_JOD, self.N_alpha)
        with tqdm(total=len(self.PODs)*len(self.PEA)*len(self.imgs)*(self.N_alpha + 3)) as pbar:
            for pod in self.PODs:
                ret_d[pod.name] = {}
                for pea in self.PEA:
                    
                    # plot user study results
                    self.plot_measurements(pea, pod, pbar)
                    
                    alphas = pea.get_Weibull().inv(utils.jod_to_p_pref(-1 * jods))
                    alphas[alphas>pea.alpha_range[1]] = pea.alpha_range[1]
                    
                    dynamic_powers = []
                    j = 0
                    for alpha in alphas:
                        pod_arr = []
                        i = 0
                        for img in self.imgs:
                            img_name = self.img_pths[i].split("/")[-1].split(".")[0].replace(" ", "_")
                            save_name = "{}_{}_{}_{:05d}".format(img_name, pea.name.replace(" ", "_"), pod.name, j+1)
                            pod_arr += [pod.evaluate(pea.evaluate(img, save_name, alpha, **self.display_params))[1]]
                            pbar.update(1)
                            i += 1
                            
                        j += 1
                        dynamic_powers += [np.asarray(pod_arr)]
                    
                    savings = [(1 - power / self.ref_powers[pod.name]) * 100 for power in dynamic_powers]
                        
                    mean_powers = np.asarray([np.mean(saving) for saving in savings])
                    sem_powers = np.asarray([stats.sem(saving) for saving in savings])
                    
                    if pea.name == "Dichoptic Dimming":
                        mean_powers *= 0.5
                        
                    idx_dashed = np.where(alphas >= pea.alpha_range[1])[0]
                    if len(idx_dashed) > 0:
                        idx_dashed = np.append([idx_dashed[0] - 1], idx_dashed)
                    idx_solid = np.where(alphas < pea.alpha_range[1])[0]
                        
                    plt.plot(jods[idx_solid], mean_powers[idx_solid], label=pea.name, color=pea.color)
                    plt.plot(jods[idx_dashed], mean_powers[idx_dashed], color=pea.color, linestyle="--")
                    plt.fill_between(jods, mean_powers - sem_powers, mean_powers + sem_powers, color=pea.color, alpha=.4)
                    
                    ret_d[pod.name][pea.name] = {
                        "jods": jods,
                        "mean_powers": mean_powers
                    }
                
                plt.legend()
                plt.xlabel("Perceptual Impact [JODs]")
                plt.ylabel("Power Savings [%]")
                plt.ylim(0, 50)
                plt.xlim([.1, min_JOD])
                plt.title("{}".format(pod.name))
                plt.savefig("{}/plots/{}.pdf".format(self.save_pth, "".join(pod.name.split(" "))), dpi=300, bbox_inches="tight")
                plt.close()
        return ret_d