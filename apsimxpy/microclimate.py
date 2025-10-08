import json
from .utils import ApsimModifier

class MicroClimate(ApsimModifier):
    def __init__(self,init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        self.zone = next(child for child in children if child["$type"] == "Models.MicroClimate, Models")
        self.__a_inter = self.zone['a_interception']
        self.__b_inter = self.zone['b_interception']
        self.__c_inter = self.zone['c_interception']
        self.__d_inter = self.zone['d_interception']
        self.__SoilHeatFluxFraction = self.zone['SoilHeatFluxFraction']
        self.__MinimumHeightDiffForNewLayer=self.zone['MinimumHeightDiffForNewLayer']
        self.__NightInterceptionFraction=self.zone['NightInterceptionFraction']
        self.__ReferenceHeight=self.zone['ReferenceHeight']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        self.zone = next(child for child in children if child["$type"] == "Models.MicroClimate, Models")
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    
    #Setter's
    def set_a_inter(self,new_a_inter):
        self._reload()
        self.zone['a_interception']=new_a_inter
        self.save_changes()
        self.__a_inter = self.zone['a_interception']
    
    def set_b_inter(self,new_b_inter):
        self._reload()
        self.zone['b_interception']=new_b_inter
        self.save_changes()  
        self.__b_inter = self.zone['b_interception']
        
    
    def set_c_inter(self,new_c_inter):
        self._reload()
        self.zone['c_interception']=new_c_inter
        self.save_changes()   
        self.__c_inter = self.zone['c_interception']
        
    
    def set_d_inter(self,new_d_inter):
        self._reload()
        self.zone['d_interception']=new_d_inter
        self.save_changes()   
        self.__d_inter = self.zone['d_interception']
    
    def set_SoilHeatFluxFraction(self,new_shff):
        self._reload()
        self.zone['SoilHeatFluxFraction']=new_shff
        self.save_changes()
        self.__SoilHeatFluxFraction = self.zone['SoilHeatFluxFraction']
    
    def set_MinimumHeightDiffForNewLayer (self,new_mhdfnl):
        self._reload()
        self.zone['MinimumHeightDiffForNewLayer']=new_mhdfnl
        self.save_changes()
        self.__MinimumHeightDiffForNewLayer=self.zone['MinimumHeightDiffForNewLayer']
    
    def set_NightInterceptionFraction (self,new_nif):
        self._reload()
        self.zone['NightInterceptionFraction']=new_nif
        self.save_changes()
        self.__NightInterceptionFraction=self.zone['NightInterceptionFraction']
    
    def set_ReferenceHeight(self,new_rh):
        self._reload()
        self.zone['ReferenceHeight']=new_rh
        self.save_changes()
        self.__ReferenceHeight=self.zone['ReferenceHeight']
        
    
    #Getter's
    def get_a_inter(self):
        return f'Multiplier on rainfall to calculate interception losses: {self.__a_inter}'       
    def get_b_inter(self):
        return f'Power on rainfall to calculate interception losses (mm) {self.__b_inter } ' 
    def get_c_inter(self):
        return f'Multiplier on LAI to calculate interception losses (mm): {self.__c_inter } ' 
    def get_d_inter(self):
        return f'Constant value to add to calculate interception lossses (mm): {self.__d_inter }' 
    def get_SoilHeatFluxFraction(self):
        return f'Fraction of solar radiation reaching the soil surface the results in soil heating (MJ/MJ): {self.__SoilHeatFluxFraction }'
    def get_MinimumHeightDiffForNewLayer (self):
        return f'The minimun height difference between canopies for a new layer to be created: {self.__MinimumHeightDiffForNewLayer }'
    def get_NightInterceptionFraction (self):
        return f'The fraction of intercepted rainfall that evaporates at night (0-1): {self.__NightInterceptionFraction }'
    def get_ReferenceHeight(self):
        return f'Height of the weather instruments (m) {self.__ReferenceHeight}'
        