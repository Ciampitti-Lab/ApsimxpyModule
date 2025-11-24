import json
import pandas as pd
import numpy as np 
import geopandas as gpd
import shapely
import contextlib
from .ssurgo import sdapoly, sdaprop, sdainterp
from .chemical import Chemical
from .physical import Physical, PhysicalCrop
from .soil_water import SoilWater
from .water import Water
from .organic import Organic
from ...utils import ApsimModifier

class Soil(ApsimModifier):
    def __init__(self,init_obj=None):
        self.init_obj=init_obj
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        self.Soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models") 
        
        self.__RecordNumber=self.Soil['RecordNumber']
        self.__ASCOrder=self.Soil['ASCOrder']
        self.__ASCSubOrder=self.Soil['ASCSubOrder']
        self.__SoilType=self.Soil['SoilType']
        self.__LocalName=self.Soil['LocalName']
        self.__Site=self.Soil['Site']
        self.__NearestTown=self.Soil['NearestTown']
        self.__Region=self.Soil['Region']
        self.__State=self.Soil['State']
        self.__Country=self.Soil['Country']
        self.__ApsoilNumber=self.Soil['ApsoilNumber']
        self.__Longitude=self.Soil['Longitude']
        self.__Latitude=self.Soil['Latitude']
        self.__LocationAccuracy=self.Soil['LocationAccuracy']
        self.__YearOfSampling=self.Soil['YearOfSampling']
        self.__DataSource=self.Soil['DataSource']
        self.__Comments=self.Soil['Comments']
        self.__Name=self.Soil['Name']
        self.__ResourceName=self.Soil['ResourceName']

    def _reload(self):
            apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
            apsim_json = apsim_file.read()
            self.modifier=json.loads(apsim_json)
            children = self.modifier["Children"][0]["Children"]
            zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
            self.Soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        
    def save_changes(self):
            with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
                json.dump(self.modifier, f, indent=4)  
    

    def __soil_variable_profile(self, nlayers, a=0.5, b=0.5):
        """
        Generate a soil profile based on the Ricker function or exponential decay.
        """
        if a < 0:
            raise ValueError("a parameter cannot be negative")
        
        layers = np.arange(1, nlayers + 1)  # 1:nlayers
        
        if a > 0 and b != 0:
            tmp = a * layers * np.exp(-b * layers)
            ans = tmp / tmp.max()
            
        elif a == 0 and b != 0:
            ans = np.exp(-b * layers) / np.exp(-b)
            
        elif a == 0 and b == 0:
            ans = np.ones(nlayers)
        
        return ans

# Setters 
    def set_soil_saxton(self,soil_saxton):
        soil_phy=Physical(self.init_obj)
        soil_phy_crop=PhysicalCrop(self.init_obj)
        soil_org=Organic(self.init_obj)
        soil_che=Chemical(self.init_obj)
        soil_wat=Water(self.init_obj)
        SW_soil_wat=SoilWater(self.init_obj)
        ###################### THICKNESS ############################################################################
        soil_phy.set_Thickness(list(soil_saxton['THICK']))
        soil_che.set_Thickness(list(soil_saxton['THICK']))
        
        thickness = soil_phy.get_Thickness()
        
        self._reload()
        waterb = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.WaterModel.WaterBalance, Models")
        water = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Water, Models")
        organ = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Organic, Models")
        chemical = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Chemical, Models")
        
        organ['Thickness']=water['Thickness']=waterb['Thickness']=chemical['Thickness']=thickness
        self.save_changes()  
        #############################################################################################################
        soil_phy.set_ParticleSizeSand(list(soil_saxton['SAND']))
        soil_phy.set_ParticleSizeClay(list(soil_saxton['CLAY']))
        soil_phy.set_ParticleSizeSilt(list(soil_saxton['SILT']))
        soil_phy.set_BD(list(soil_saxton['BD']))
        soil_phy.set_AirDry(list(soil_saxton['AirDry']))
        soil_phy.set_DUL(list(soil_saxton['DUL']))
        soil_phy.set_LL15(list(soil_saxton['LL']))
        soil_phy.set_SAT(list(soil_saxton['SAT']))
        soil_org.set_Carbon(list(soil_saxton['CO']))
        soil_che.set_cec(list(soil_saxton['CO']))
        soil_org.set_SoilCNRatio(list(soil_saxton['SoilCN']))
        soil_org.set_FBiom(list(soil_saxton['FBiom']))
        soil_org.set_FInert(list(soil_saxton['FIner']))
        soil_che.set_ph(list(soil_saxton['PH']))
        soil_che.set_nh4_initial_values(list(soil_saxton['PH']))
        soil_che.set_no3_initial_values(list(soil_saxton['no3kgha']))
        soil_che.set_urea_initial_values([0.0 for _ in soil_phy.get_Thickness()])
        soil_phy_crop.set_kl(list(soil_saxton['KL_maize']))
        soil_phy_crop.set_ll(list(soil_saxton['LL']))
        soil_phy_crop.set_xf(list(soil_saxton['XF_maize']))    
        SW_soil_wat.set_SWCON(list(soil_saxton['SWCON']))   
        soil_phy.set_KS(list(soil_saxton['KSAT'])) 
        soil_org.set_FOM([round(x, 4) for x in 40 * self.__soil_variable_profile(len(thickness),a=0,b=0)])   
        soil_wat.set_InitialValues(list(soil_saxton['DUL']))
        
    def set_Soil_Fmiguez(self,soil_df):
        ###################### CHECKING ############################################################################
        cond_texture = ((soil_df["Sand"] == 0) & (soil_df["Silt"] == 0) & (soil_df["Clay"] == 0)| (soil_df[["Sand", "Silt", "Clay"]].isna().all(axis=1)))
        cond_texture_correct = ~cond_texture

        
        if cond_texture.any()==True:
            if cond_texture_correct.any()==True:
                soil_df.loc[cond_texture, ["Sand", "Silt", "Clay"]] = soil_df.loc[cond_texture_correct, ["Sand", "Silt", "Clay"]].iloc[0].tolist()
            else:
                print('No texture :( ')
                soil_df.loc[cond_texture, ["Sand", "Silt", "Clay"]] = [60,15,25]
            
        
        cond_phy=((soil_df['AirDry'].isna())|(soil_df['LL15'].isna())|(soil_df['DUL'].isna())|(soil_df['SAT'].isna())|(soil_df['BD'].isna()))
        cond_phy_correct = ~cond_phy
        
        
        if cond_phy.any()==True:
            if cond_phy_correct.any()==True:
                soil_df.loc[cond_phy, ["AirDry", "LL15", "DUL","SAT","BD","WaterInitialValues"]]=soil_df.loc[cond_phy_correct, ["AirDry", "LL15", "DUL","SAT","BD","WaterInitialValues"]].iloc[0].tolist()
            else:
                print('No Soil Values :(')
                soil_df.loc[cond_phy, ["AirDry", "LL15", "DUL","SAT","BD","WaterInitialValues"]] = [float(0.1 * self.__soil_variable_profile(1,a=0,b=0.2)),
                                                                        float(0.15 * self.__soil_variable_profile(1,a=0,b=0.2)),
                                                                        float(0.25 * self.__soil_variable_profile(1,a=0,b=0.2)),
                                                                        float(0.45 * self.__soil_variable_profile(1,a=0,b=0.2)),
                                                                        float(1.1 * self.__soil_variable_profile(1,a=0,b=-0.05)),
                                                                        float(0.15 * self.__soil_variable_profile(1,a=0,b=0.2))]    
        print(soil_df)
        ###################### THICKNESS ############################################################################
        soil_phy=Physical(self.init_obj)
        soil_phy_crop=PhysicalCrop(self.init_obj)
        soil_org=Organic(self.init_obj)
        soil_che=Chemical(self.init_obj)
        soil_wat=Water(self.init_obj)
        SW_soil_wat=SoilWater(self.init_obj)
        
        # print(soil_df['Sand'])
        soil_phy.set_Thickness(list(soil_df['hzdepb_r']))
        soil_che.set_Thickness(list(soil_df['hzdepb_r']))
        
        thickness = soil_phy.get_Thickness()
        
        self._reload()
        waterb = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.WaterModel.WaterBalance, Models")
        water = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Water, Models")
        organ = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Organic, Models")
        chemical = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Chemical, Models")
        
        organ['Thickness']=water['Thickness']=waterb['Thickness']=chemical['Thickness']=thickness
        self.save_changes()
        ###############################################################################################################
        
        soil_phy.set_ParticleSizeSand(list(soil_df['Sand']))
        soil_phy.set_ParticleSizeSilt(list(soil_df['Silt']))
        soil_phy.set_ParticleSizeClay(list(soil_df['Clay']))
        soil_phy.set_BD(list(soil_df['BD']))
        soil_phy.set_SAT(list(soil_df['SAT']))
        soil_phy.set_DUL(list(soil_df['DUL']))
        soil_phy.set_LL15(list(soil_df['LL15']))
        soil_phy.set_AirDry(list(soil_df['AirDry']))
        
        
        soil_org.set_Carbon(list(soil_df['Carbon']))
        soil_che.set_cec(list(soil_df['CEC']))
        soil_org.set_SoilCNRatio(list(soil_df['SoilCNRatio']))
        soil_wat.set_InitialValues(list(soil_df['WaterInitialValues']))
        
        # FInert FBiom NH4 NO3 KS PH FOM
        
        
        PH_list=[round(x, 4) for x in 6.5 * self.__soil_variable_profile(len(thickness),a=0,b=0)]
        FOM_list=[round(x, 4) for x in 40 * self.__soil_variable_profile(len(thickness),a=0,b=0)]
        FBiom_list=[round(x, 4) for x in 0.04 * self.__soil_variable_profile(len(thickness),a=0,b=0.2)]
        FInert_list=[round(x, 4) for x in 0.8 * self.__soil_variable_profile(len(thickness),a=0,b=-0.01)]
        nh4_list = [300.0 for _ in soil_phy.get_Thickness()]
        no3_list = [300.0 for _ in soil_phy.get_Thickness()]
        ks_list = [round(x, 4) for x in 100 * self.__soil_variable_profile(len(thickness),a=0,b=0.2)]
        swcon_list=[0.3]*len(thickness)
        
        # Crop         
        ll_list = soil_phy.get_LL15()
        kl_list = [round(x, 4) for x in 0.06 * self.__soil_variable_profile(len(thickness),a=0,b=0.2)]
        xf_list = [round(x, 4) for x in 1 * self.__soil_variable_profile(len(thickness),a=0,b=0)]
        
        urea_list = [0.0 for _ in soil_phy.get_Thickness()]
        
        
        soil_phy.set_KS(ks_list)
        soil_org.set_FOM(FOM_list)
        soil_org.set_FBiom(FBiom_list)
        soil_org.set_FInert(FInert_list)
        soil_che.set_ph(PH_list)
        soil_che.set_nh4_initial_values(nh4_list)
        soil_che.set_no3_initial_values(no3_list)
        soil_che.set_urea_initial_values(urea_list)
        soil_phy_crop.set_kl(kl_list)
        soil_phy_crop.set_ll(ll_list)
        soil_phy_crop.set_xf(xf_list)
        # Rocks -- Null
        # SWCON Values from the MaizeSoybean apsim file       
        SW_soil_wat.set_SWCON(swcon_list)
        print('Soil established successfully')

        

        
    def set_RecordNumber(self, new_value):
        self._reload()
        self.Soil['RecordNumber']=new_value
        self.save_changes()
        self.__RecordNumber=self.Soil['RecordNumber']
        
    def set_ASCOrder(self, new_value):
        self._reload()
        self.Soil['ASCOrder']=new_value
        self.save_changes()
        self.__ASCOrder=self.Soil['ASCOrder']     
        
    def set_ASCSubOrder(self, new_value):
        self._reload()
        self.Soil['ASCSubOrder']=new_value
        self.save_changes()
        self.__ASCSubOrder=self.Soil['ASCSubOrder'] 

    def set_SoilType(self, new_value):
        self._reload()
        self.Soil['SoilType']=new_value
        self.save_changes()
        self.__SoilType=self.Soil['SoilType']

    def set_LocalName(self, new_value):
        self._reload()
        self.Soil['LocalName']=new_value
        self.save_changes()
        self.__LocalName=self.Soil['LocalName']
         
    def set_Site(self, new_value):
        self._reload()
        self.Soil['Site']=new_value
        self.save_changes()
        self.__Site=self.Soil['Site']
         
    def set_NearestTown(self, new_value):
        self._reload()
        self.Soil['NearestTown']=new_value
        self.save_changes()
        self.__NearestTown=self.Soil['NearestTown']
        
    def set_Region(self, new_value):
        self._reload()
        self.Soil['Region']=new_value
        self.save_changes()
        self.__Region=self.Soil['Region']
        
    def set_State(self, new_value):
        self._reload()
        self.Soil['State']=new_value
        self.save_changes()
        self.__State=self.Soil['State']
        
    def set_Country(self, new_value):
        self._reload()
        self.Soil['Country']=new_value
        self.save_changes()
        self.__Country=self.Soil['Country']
        
    def set_ApsoilNumber(self, new_value):
        self._reload()
        self.Soil['ApsoilNumber']=new_value
        self.save_changes()
        self.__ApsoilNumber=self.Soil['ApsoilNumber']
        
    def set_Longitude(self, new_value):
        self._reload()
        self.Soil['Longitude']=new_value
        self.save_changes()
        self.__Longitude=self.Soil['Longitude']
        
    def set_Latitude(self, new_value):
        self._reload()
        self.Soil['Latitude']=new_value
        self.save_changes()
        self.__Latitude=self.Soil['Latitude']
        
    def set_LocationAccuracy(self, new_value):
        self._reload()
        self.Soil['LocationAccuracy']=new_value
        self.save_changes()
        self.__LocationAccuracy=self.Soil['LocationAccuracy']
        
    def set_YearOfSampling(self, new_value):
        self._reload()
        self.Soil['YearOfSampling']=new_value
        self.save_changes()
        self.__YearOfSampling=self.Soil['YearOfSampling']
        
    def set_DataSource(self, new_value):
        self._reload()
        self.Soil['DataSource']=new_value
        self.save_changes()
        self.__DataSource=self.Soil['DataSource']
        
    def set_Comments(self, new_value):
        self._reload()
        self.Soil['Comments']=new_value
        self.save_changes()
        self.__Comments=self.Soil['Comments']
        
    def set_Name(self, new_value):
        self._reload()
        self.Soil['Name']=new_value
        self.save_changes()
        self.__Name=self.Soil['Name']
    def set_ResourceName(self, new_value):
        self._reload()
        self.Soil['ResourceName']=new_value
        self.save_changes()
        self.__ResourceName=self.Soil['ResourceName']
# Getters
    def get_RecordNumber(self):
        return f'Record Number: {self.__RecordNumber}'
    def get_ASCOrder(self):
        return f'Soil Classification Order: {self.__}'
    def get_ASCSubOrder(self):
        return f'Soil Classification Sub Order: {self.__ASCSubOrder}'
    def get_SoilType(self):
        return f'Soil texture or other descriptor: {self.__SoilType}'
    def get_LocalName(self):
        return f'Local Name: {self.__LocalName}'
    def get_Site(self):
        return f'Site: {self.__Site}'
    def get_NearestTown(self):
        return f'Nearest Town: {self.__NearestTown}'
    def get_Region(self):
        return f'Region: {self.__Region}'
    def get_State(self):
        return f'State: {self.__State}'
    def get_Country(self):
        return f'Country: {self.__Country}'
    def get_ApsoilNumber(self):
        return f'Natural vegetation: {self.__ApsoilNumber}'
    def get_Longitude(self):
        return f'APSoil number: {self.__Longitude}°'
    def get_Latitude(self):
        return f'Latitude (WGS84): {self.__Latitude}°'
    def get_LocationAccuracy(self):
        return f'Longitude (WGS84): {self.__LocationAccuracy}'
    def get_YearOfSampling(self):
        return f'Year of Sampling: {self.__YearOfSampling}'
    def get_DataSource(self):
        return f'Data Source: {self.__DataSource}'
    def get_Comments(self):
        return f'Comments: {self.__Comments}'
    def get_Name(self):
        return f'Name: {self.__Name}'
    def get_ResourceName(self):
        return f'Resource Name: {self.__ResourceName}'
    def get_Thickness(self):
        physical = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Physical, Models")
        thickness=physical['Thickness']
        return thickness
    
    