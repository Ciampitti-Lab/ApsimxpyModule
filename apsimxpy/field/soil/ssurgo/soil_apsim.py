import numpy as np
import contextlib
import pandas as pd
import apsimxpy
from apsimxpy.field.soil.ssurgo import saxton as sax
import math

# Getting available soils in a polygon from SSURGO
def soil_apsim(soil_props_surgo):
    saxton=sax.saxton_rawls(soil_props_surgo)
    # Sand, Clay, Silt
    SAND=soil_props_surgo['sandtotal_r']
    CLAY=soil_props_surgo['claytotal_r']
    SILT=soil_props_surgo['silttotal_r']
    # Bulk Density
    BD = np.where(soil_props_surgo['dbovendry_r'] < 0.9, 0.9, np.where(soil_props_surgo['dbovendry_r'] > 1.8, 1.8, soil_props_surgo['dbovendry_r']))

    # KSAT
    KSAT= np.minimum(soil_props_surgo['ksat_r'] * 100 / 1.157, saxton['KSAT']*2)
    
    
    # SAT
    SAT = saxton['SAT']
    sat_max = 1 - BD / 2.64 
    SAT = np.minimum(SAT, sat_max)
    
    # DUL
    DUL_sax=saxton['DUL']
    DUL = [dul/100 for dul in soil_props_surgo['wthirdbar_r']]
    DUL=np.minimum(DUL, DUL_sax)
    DUL = np.minimum(DUL, SAT)
    
    # LL
    LL = [ll/100 for ll in soil_props_surgo['wfifteenbar_r']]
    
    #AirDry
    AirDry = [  0.9*l if c < 15 else
                0.95*l if c <= 30 else
                l
                for c, l in zip(soil_props_surgo['center'], LL)
             ]
    # PO
    PO = [1-bd/2.65 for bd in BD]
    
    # SWCON
    SWCON=[(po - dul)/po for po, dul in zip(PO, DUL)]
    
    # U
    U = [5 + 0.175*clay if clay <= 20 else
    7.5 + 0.05*clay if clay <= 40 else
    11.5 - 0.05*clay if clay <= 50 else
    12.75 - 0.075*clay if clay <= 70 else
    11 - 0.05*clay if clay <= 80 else
    0
    for clay in CLAY]
    
    # CONA
    CONA=[
    0.025*clay + 3.25 if clay <= 30 else
    4 if clay <= 50 else
    -0.025*clay + 5.25 if clay <= 70 else
    3.5 if clay <= 80 else
    0   
    for clay in CLAY
    ]
    
    # DiffusConst
    DiffusConst=[40 for hzn in soil_props_surgo['hzdepb_r']]
    
    # DiffusSlope
    DiffusSlope=[16 for hzn in soil_props_surgo['hzdepb_r']]
    
    # CN2
    CN2=[80 for hzn in soil_props_surgo['hzdepb_r']]
    
    # CNRed
    CNRed=[20 for hzn in soil_props_surgo['hzdepb_r']]
    
    # CNCov
    CNCov=[0.8 for hzn in soil_props_surgo['hzdepb_r']]
    
    # EnrAcoeff
    EnrAcoeff=[7.4 for hzn in soil_props_surgo['hzdepb_r']]
    
    # EnrBcoeff
    EnrBcoeff=[0.2 for hzn in soil_props_surgo['hzdepb_r']]
    
    # Limit Roots
    limit_roots = 200
    
    # XF Maize
    XF_maize = [1 if bot<limit_roots else 0.1 for bot in soil_props_surgo['hzdepb_r']]
    
    # KL_maize
    KL_maize = [0.08 if c <= 20 else 0.09*math.exp(-0.007*c) for c in soil_props_surgo['center']]
    
    # e
    e = [0.5 for hzn in soil_props_surgo['hzdepb_r']]
    
    # pH
    PH = 0.52 + 1.06 * 6.5
    
    # CO
    CO = soil_props_surgo['om_r'] / 1.72
    OC_array = CO
    center_array = soil_props_surgo['center'].values
    
    for i in range(1, len(soil_props_surgo)):
        if center_array[i] >= 100 and OC_array[i] == OC_array[i-1]:
            OC_array[i] = OC_array[0] * np.exp(-0.035 * center_array[i])
    CO = OC_array   
    CO[CO == 0] = 0.001 
    
    # FBiom
    FBiom=[0.11, 0.10, 0.09, 0.08, 0.06, 0.01, 0.01, 0.005, 0.001, 0.001]
    FBiom=FBiom[0:len(soil_props_surgo['hzdepb_r'])]
    # FInert
    FIner=[0.4, 0.45, 0.55, 0.6, 0.65, 0.7, 0.8,0.9, 0.95, 0.99]
    FIner=FIner[0:len(soil_props_surgo['hzdepb_r'])]
    # RootCN
    RootCN = [45 for hzn in soil_props_surgo['hzdepb_r']]
    
    # SoilCN
    SoilCN = [13 for hzn in soil_props_surgo['hzdepb_r']]
  
    # RootWt
    RootWt = [1000 for hzn in soil_props_surgo['hzdepb_r']]
    
    # SW
    SW = DUL
    
    # Nitrogen
    no3kgha = [0 for hzn in soil_props_surgo['hzdepb_r']]
    nh4kgha = [0 for hzn in soil_props_surgo['hzdepb_r']]
    
    #CEC
    CEC = soil_props_surgo['cec7_r']
    
    # THICK
    HORIZON_LONG=[x*10 for x in soil_props_surgo['hzdepb_r']]
    
    if len(HORIZON_LONG) == 0:
        THICK = pd.Series([])
    else:
        THICK = pd.Series(HORIZON_LONG).diff().fillna(HORIZON_LONG[0])
    
    apsim_soil=pd.DataFrame(
        {'SAND':SAND,
         'CLAY':CLAY,
         'SILT':SILT,
         'BD':BD,
         'KSAT':KSAT,
         'SAT':SAT,
         'DUL':DUL,
         'LL':LL,
         'AirDry':AirDry,
         'PO':PO,
         'SWCON':SWCON,
         'CONA':CONA,
         'DiffusConst':DiffusConst,
         'XF_maize':XF_maize,
         'KL_maize':KL_maize,
         'e' : e,
         'PH':PH,
         'CO':CO,
         'FBiom':FBiom,
         'FIner':FIner,
         'RootCN':RootCN,
         'SoilCN':SoilCN,
         'RootWt':RootWt,
         'SW':SW,
         'no3kgha':no3kgha,
         'nh4kgha':nh4kgha,
         'CEC': CEC,
         'THICK':THICK
         }
    )
    return apsim_soil


    

        
        
    
    
