# ************************************
# Functions to calculate soil hydraulic parameters
# Ref. Saxton & Rawls, 2006
# ************************************
import pandas as pd
import numpy as np


def saxton_rawls(soil_props_ssurgo)-> pd.DataFrame:
    
    cols = ['claytotal_r', 'sandtotal_r', 'om_r']

    for c in cols:
        soil_props_ssurgo[c] = pd.to_numeric(soil_props_ssurgo[c], errors='coerce')
    
    Sand=soil_props_ssurgo['sandtotal_r']
    Clay=soil_props_ssurgo['claytotal_r']
    OM=soil_props_ssurgo['om_r']
    Thickness=soil_props_ssurgo['thickness']
    
    pSand = Sand/100
    pClay = Clay/100
    pOM = OM/100
    
    
    # calc LL15 (theta_1500)
    theta_1500t = -0.024*pSand + 0.487*pClay + 0.006*pOM + 0.005*pSand*pOM - 0.013*pClay*pOM + 0.068*pSand*pClay + 0.031
    LL15 = theta_1500t + (0.14*theta_1500t - 0.02)
    LL15 = np.round(np.clip(LL15, 0.01, 0.99), 3)
    
    
    # calc DUL (theta_33)
    theta_33t = -0.251*pSand + 0.195*pClay + 0.011*pOM +0.006*pSand*pOM - 0.027*pClay*pOM + 0.452*pSand*pClay + 0.299
    DUL = theta_33t + (1.283*theta_33t**2 - 0.374*theta_33t - 0.015)
    DUL = np.round(np.clip(DUL, 0.01, 0.99), 3)
    
    # calc SAT-33 KPa moisture
    theta_sat33t = 0.278*pSand + 0.034*pClay + 0.022*pOM -0.018*pSand*pOM - 0.027*pClay*pOM - 0.584*pSand*pClay + 0.078
    theta_sat33 = theta_sat33t + (0.636*theta_sat33t - 0.107)
    
    # calc SAT
    SAT = DUL + theta_sat33 - 0.097*pSand + 0.043
    SAT = np.round(np.clip(SAT, 0.01, 0.99), 3)
    
    # calc BD
    BD = (1 - SAT)*2.65
    BD = np.round(np.clip(BD, 1, 2.1), 3)
    
    # calc ksat (saturated water conductivity)
    lam = (np.log(DUL)-np.log(LL15)) / (np.log(1500)-np.log(33))
    ksat = 1930*((SAT-DUL)**(3-lam))
    SWCON = np.round(0.15 + np.minimum(ksat, 75) / 100, 3)
    
    saxton_soil=pd.DataFrame({"BD": BD,
    "LL15": LL15,
    "DUL": DUL,
    "SAT": SAT,
    "SWCON": SWCON,
    "KSAT": ksat,
    "Thickness":Thickness
    })
    
    return saxton_soil