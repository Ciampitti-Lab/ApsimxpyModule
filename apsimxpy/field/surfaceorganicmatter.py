from ..utils import ApsimModifier
import json


class SOM(ApsimModifier):
    def __init__(self, init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)

        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        self.SOM = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Surface.SurfaceOrganicMatter, Models")
    
        self.__InitialResidueName = self.SOM['InitialResidueName']
        self.__InitialResidueType = self.SOM['InitialResidueType']
        self.__InitialResidueMass = self.SOM['InitialResidueMass']
        self.__InitialCPR = self.SOM['InitialCPR']
        self.__InitialCNR = self.SOM['InitialCNR']


        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        self.SOM = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Surface.SurfaceOrganicMatter, Models")
    
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    
    # Setters        
    def set_initialresiduename(self,new_value):
        self._reload()
        self.SOM['InitialResidueName']=new_value
        self.save_changes()
        self.__InitialResidueName = self.SOM['InitialResidueName']
        
    def set_initialresiduetype(self,new_value):
        self._reload()
        self.SOM['InitialResidueType']=new_value
        self.save_changes()
        self.__InitialResidueType = self.SOM['InitialResidueType']


    def set_initialresiduemass(self,new_value):
        self._reload()
        self.SOM['InitialResidueMass']=new_value
        self.save_changes()
        self.__InitialResidueMass = self.SOM['InitialResidueMass']
        

    def set_initialcpr(self,new_value):
        self._reload()
        self.SOM['InitialCPR']=new_value
        self.save_changes()
        self.__InitialCPR = self.SOM['InitialCPR']

    def set_initialcnr(self,new_value):
        self._reload()
        self.SOM['InitialCNR']=new_value
        self.save_changes()
        self.__InitialCNR = self.SOM['InitialCNR']

    # Getters    
    
    def get_initialresiduename(self):
        return f'Name of the intitial residue pool: {self.__InitialResidueName}'
    def get_initialresiduetype(self):
        return f'Type of the initial residue pool: {self.__InitialResidueType}'
    def get_initialresiduemass(self):
        return f'Mass of initial surface residue (kg/ha): {self.__InitialResidueMass}'
    def get_initialcpr(self):
        return f'Carbon_Phosphorus ratio (g/g): {self.__InitialCPR}'
    def get_initialcnr(self):
        return f'Carbon-Nitrogen ratio (g/g): {self.__InitialCNR}'
    
    