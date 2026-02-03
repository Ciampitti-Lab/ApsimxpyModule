import json 
from ...utils import ApsimModifier

class Fertilize(ApsimModifier):
    def __init__(self, init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        params = next(prop for prop in zones['Children'] if prop["Name"] == "FertiliseSowing")['Parameters']
        amount = next(param for param in params if param["Key"] == "Amount")
        
        self.__fert_sowing=amount['Value']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        self.params = next(prop for prop in zones['Children'] if prop["Name"] == "FertiliseSowing")['Parameters']
        
    
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Field attributes to get and set     
    def set_fert_sowing(self,new_value):
        self._reload()
        amount = next(param for param in self.params if param["Key"] == "Amount")
        amount['Value'] = str(new_value)  
        self.save_changes()  
        self.__fert_sowing=new_value

        
    def get_fert_sowing(self):
        return self.__fert_sowing