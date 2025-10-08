import json
import pandas as pd
import numpy as np 
import geopandas as gpd
import shapely
import contextlib
from .ssurgo import sdapoly, sdaprop, sdainterp
from .chemical import Chemical
from .physical import Physical
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
        
# Setters 
    def set_Soil(self,latlon): # Latlong is a tuple
        
        self._reload()
        
        longitude = latlon[1]
        latitude = latlon[0]

        point_geom = shapely.Point(longitude, latitude)



        gdf = gpd.GeoDataFrame({'name': ['MyPoint']},
                            geometry=[shapely.Point(longitude, latitude)],
                            crs="EPSG:4326")

        gdf_utm = gdf.to_crs(epsg=32616) 


        poly_geom = gdf_utm.geometry[0].buffer(1) 

        gdf_buffer = gpd.GeoDataFrame({'name': ['MyPoint']}, geometry=[poly_geom], crs=gdf_utm.crs)

        with contextlib.redirect_stdout(None):
            myaoi = sdapoly.gdf(gdf_buffer)

            apsim_props = [
                'sandtotal_r', 'silttotal_r', 'claytotal_r',  # Sand, Silt, Clay
                'om_r',                                        # Carbon
                'dbovendry_r',  # BD
                'wtenthbar_r', 'wthirdbar_r', 'wfifteenbar_r', 'wsatiated_r', # AirDry , DUL, LL15, SAT
                'ksat_r',                                      # SWCON
                'cec7_r' # CEC
            ]

            soil_df=pd.DataFrame()

            for j,i in enumerate(apsim_props) :
                if j==0:
                    try:
                        wtdavg=sdaprop.getprop(df=myaoi,column='mukey',method='wtd_avg',prop=i,minmax=None,prnt=False,meta=False)
                        print(wtdavg)
                        soil_df['mukey']=wtdavg['mukey']
                        soil_df['musym']=wtdavg['musym']
                        soil_df['hzdept_r']=wtdavg['hzdept_r']
                        soil_df['hzdepb_r']=wtdavg['hzdepb_r']
                        soil_df[i]=wtdavg[i]
                    except:
                        wtdavg=sdaprop.getprop(df=myaoi,column='mukey',method='minmax',prop=i,minmax='max',prnt=False,meta=False)
                        soil_df['mukey']=wtdavg['mukey']
                        soil_df['musym']=wtdavg['musym']
                        soil_df['hzdept_r']=wtdavg['hzdept_r']
                        soil_df['hzdepb_r']=wtdavg['hzdepb_r']
                        soil_df[i]=wtdavg[i]
                else:
                    try:
                        wtdavg=sdaprop.getprop(df=myaoi,column='mukey',method='wtd_avg',prop=i,minmax=None,prnt=False,meta=False)
                        soil_df[i]=wtdavg[i]
                    except:
                        wtdavg=sdaprop.getprop(df=myaoi,column='mukey',method='minmax',prop=i,minmax='max',prnt=False,meta=False)
                        soil_df[i]=wtdavg[i]

        soil_df['thickness']=soil_df['hzdept_r'].astype(str)+'-'+soil_df['hzdepb_r'].astype(str)
        soil_df=soil_df[['sandtotal_r','silttotal_r','claytotal_r','om_r','dbovendry_r','wtenthbar_r','wthirdbar_r','wfifteenbar_r','wsatiated_r','ksat_r','cec7_r','thickness','hzdepb_r']]
        soil_df.columns=['Sand','Silt','Clay','Carbon','BD','AirDry','DUL','LL15','SAT','SWCON','CEC','thickness','hzdepb_r']

        # Percentaje --> Decimal
        soil_df['DUL']=[round(float(d)/100,3) for d in soil_df['DUL']]
        soil_df['LL15']=[round(float(l)/100,3) for l in soil_df['LL15']]
        soil_df['SAT']=[round(float(s)/100,3) for s in soil_df['SAT']]
        # Fix Saturation-Porosity
        poro=[1-float(bd)/2.65 - 0.001 for bd in soil_df['BD']]
        soil_df['SAT']=np.where(np.array(poro) < soil_df['SAT'], poro, soil_df['SAT'])
        soil_df['DUL']=np.where(np.array(soil_df['SAT']) < soil_df['DUL'], soil_df['SAT'], soil_df['DUL'])
        soil_df['LL15']=np.where(np.array(soil_df['DUL']) < soil_df['LL15'], soil_df['DUL'], soil_df['LL15'])
        # Calculating AirDry
        soil_df['AirDry']=[l*0.5 for l in soil_df['LL15']] 
        # SoilCNRatio
        soil_df['SoilCNRatio']=['12']*soil_df.shape[0]
        # WaterInitialValues
        soil_df['WaterInitialValues']=soil_df['LL15']
    
        
        soil_phy=Physical(self.init_obj)
        soil_org=Organic(self.init_obj)
        soil_che=Chemical(self.init_obj)
        soil_wat=Water(self.init_obj)
        soil_phy.set_ParticleSizeSand(list(soil_df['Sand']))
        soil_phy.set_ParticleSizeSilt(list(soil_df['Silt']))
        soil_phy.set_ParticleSizeClay(list(soil_df['Clay']))
        soil_phy.set_AirDry(list(soil_df['AirDry']))
        soil_org.set_Carbon(list(soil_df['Carbon']))
        soil_phy.set_BD(list(soil_df['BD']))
        soil_phy.set_AirDry(list(soil_df['AirDry']))
        soil_phy.set_DUL(list(soil_df['DUL']))
        soil_phy.set_LL15(list(soil_df['LL15']))
        soil_phy.set_SAT(list(soil_df['SAT']))
        soil_che.set_cec(list(soil_df['CEC']))
        soil_org.set_SoilCNRatio(list(soil_df['SoilCNRatio']))
        soil_wat.set_InitialValues(list(soil_df['WaterInitialValues']))
        # SWCON ?
        # pH?
        
        self.set_Thickness(list(soil_df['hzdepb_r']))
        
        print('Soil established successfully')

        
        
        
    # I need to change this using the already created objects
    def set_Thickness(self,new_list):
        self._reload()
        # Physical, Water Balance, Water and Organic
        physical = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Physical, Models")
        waterb = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.WaterModel.WaterBalance, Models")
        water = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Water, Models")
        organ = next(prop for prop in self.Soil['Children'] if prop["$type"] == "Models.Soils.Organic, Models")
        
        # Chemical
        solutes = [child for child in self.Soil["Children"] if child["$type"] == "Models.Soils.Solute, Models"]
        no3 = next(solute for solute in solutes if solute["Name"] == "NO3")
        nh4 = next(solute for solute in solutes if solute["Name"] == "NH4")
        urea = next(solute for solute in solutes if solute["Name"] == "Urea")
        
        urea['Thickness']=no3['Thickness']=nh4['Thickness']=organ['Thickness']=water['Thickness']=waterb['Thickness']=physical['Thickness']=new_list
        print('New depht/tickness established successful')
        self.save_changes()
        
        
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
        return f'Thickness: {thickness}'
    
    