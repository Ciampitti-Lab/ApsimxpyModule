import json 
from ...utils import ApsimModifier

class Management(ApsimModifier):
    def __init__(self, init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        params = next(prop for prop in zones['Children'] if prop["Name"] == "MaizeManager")['Parameters']
        start_date = next(param for param in params if param["Key"] == "StartDate")
        end_date = next(param for param in params if param["Key"] == "EndDate")
        
        self.__start_date=start_date['Value']
        self.__end_date=end_date['Value']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        self.params = next(prop for prop in zones['Children'] if prop["Name"] == "MaizeManager")['Parameters']
        
    
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Field attributes to get and set     
    def set_start_sowing(self,new_value):
        self._reload()
        
        start_date = next(param for param in self.params if param["Key"] == "StartDate")
        
        self.save_changes()  
        self.__start_date=new_value

    def set_end_sowing(self,new_value):
        self._reload()
        
        end_date = next(param for param in self.params if param["Key"] == "EndDate")
        
        self.save_changes()  
        self.__end_date=new_value


        
    def get_start_sowing(self):
        return self.__start_date
    
    def get_end_sowing(self):
        return self.__end_date
    