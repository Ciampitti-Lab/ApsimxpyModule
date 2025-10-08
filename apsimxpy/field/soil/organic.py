import json
from ...utils import ApsimModifier

class Organic(ApsimModifier):
    def __init__(self,init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        organ = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Organic, Models")
        
        self.__FOMCNRatio=organ['FOMCNRatio']
        self.__Carbon=organ['Carbon']
        self.__CarbonUnits=organ['CarbonUnits']
        self.__SoilCNRatio=organ['SoilCNRatio']
        self.__FBiom=organ['FBiom']
        self.__FInert=organ['FInert']
        self.__FOM=organ['FOM']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.organ = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Organic, Models")
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4) 
    # Setters
    def set_FOMCNRatio(self,new_value):
        self._reload()
        self.organ['FOMCNRatio']=new_value
        self.save_changes()  
        self.__FOMCNRatio=self.organ['FOMCNRatio']
        
    def set_Carbon(self,new_list):
        self._reload()
        self.organ['Carbon']=new_list
        self.save_changes()
        self.__Carbon=self.organ['Carbon']
        
    def set_CarbonUnits(self,new_list):
        self._reload()
        self.organ['CarbonUnits']=new_list
        self.save_changes()
        self.__CarbonUnits=self.organ['CarbonUnits']
        
    def set_SoilCNRatio(self,new_list):
        self._reload()
        self.organ['SoilCNRatio']=new_list
        self.save_changes()
        self.__SoilCNRatio=self.organ['SoilCNRatio']
        
    def set_FBiom(self,new_list):
        self._reload()
        self.organ['FBiom']=new_list
        self.save_changes()
        self.__FBiom=self.organ['FBiom']
            
    def set_FInert(self,new_list):
        self._reload()
        self.organ['FInert']=new_list
        self.save_changes()
        self.__FInert=self.organ['FInert']
    
    def set_FOM(self,new_list):
        self._reload()
        self.organ['FOM']=new_list
        self.save_changes()
        self.__FOM=self.organ['FOM']
    
    # Getters
    def get_FOMCNRatio(self):
        return f'FOM C:N ratio (0-500) {self.__FOMCNRatio}'
        
    def get_Carbon(self):
        return f'Carbon: {self.__Carbon}'
        
    def get_CarbonUnits(self):
        return f'Carbon Units: {self.__CarbonUnits}'
        
    def get_SoilCNRatio(self):
        return f'SoilCNRatio: {self.__SoilCNRatio}'
        
    def get_FBiom(self):
        return f'FBiom {self.__FBiom}'
            
    def get_FInert(self):
        return f'FInert: {self.__FInert}'
    
    def get_FOM(self):
        return f'FOM: {self.__FOM}'    
        