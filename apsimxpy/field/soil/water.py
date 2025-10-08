import json
from ...utils import ApsimModifier

class Water(ApsimModifier):
    def __init__(self, init_obj):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        water = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Water, Models")
    
        self.__InitialValues=water['InitialValues']
        self.__FilledFromTop=water['FilledFromTop']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.water = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Water, Models")
        
        
    def save_changes(self):   
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
            
    #Setters
    def set_InitialValues(self,new_list):
        self._reload()
        self.water['InitialValues']=new_list
        self.save_changes()
        self.__InitialValues=self.water['InitialValues']
        
    def set_FilledFromTop(self,new_bool):
        self._reload()
        self.water['FilledFromTop']=new_bool
        self.save_changes()
        self.__FilledFromTop=self.water['FilledFromTop']
    
    #Getters
    def get_InitialValues(self):
        return f'Initial Values: {self.__InitialValues}'
    
    def get_FilledFromTop(self):
        return f'Filled From Top: {self.__FilledFromTop}'
    
        