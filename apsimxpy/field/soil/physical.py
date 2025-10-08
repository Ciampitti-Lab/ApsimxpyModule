import json
from ...utils import ApsimModifier

class Physical(ApsimModifier):
    def __init__(self, init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.physical = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Physical, Models")
        
        self.__Thickness=self.physical['Thickness']
        self.__ParticleSizeSand=self.physical['ParticleSizeSand']
        self.__ParticleSizeSilt=self.physical['ParticleSizeSilt']
        self.__ParticleSizeClay=self.physical['ParticleSizeClay']
        self.__Rocks=self.physical['Rocks']
        self.__Texture=self.physical['Texture']
        self.__BD=self.physical['BD']
        self.__AirDry=self.physical['AirDry']
        self.__LL15=self.physical['LL15']
        self.__DUL=self.physical['DUL']
        self.__SAT=self.physical['SAT']
        self.__KS=self.physical['KS']

    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.physical = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Physical, Models")
        
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Setters
    def set_Thickness(self,new_list):
        self._reload()
        self.physical['Thickness']=new_list
        self.save_changes()
        self.__Thickness=self.physical['Thickness']

    def set_ParticleSizeSand(self,new_list):
        self._reload()
        self.physical['ParticleSizeSand']=new_list
        self.save_changes()
        self.__ParticleSizeSand=self.physical['ParticleSizeSand']

    def set_ParticleSizeSilt(self,new_list):
        self._reload()
        self.physical['ParticleSizeSilt']=new_list
        self.save_changes()
        self.__ParticleSizeSilt=self.physical['ParticleSizeSilt']

    def set_ParticleSizeClay(self,new_list):
        self._reload()
        self.physical['ParticleSizeClay']=new_list
        self.save_changes()
        self.__ParticleSizeClay=self.physical['ParticleSizeClay']

    def set_Rocks(self,new_list):
        self._reload()
        self.physical['Rocks']=new_list
        self.save_changes()
        self.__Rocks=self.physical['Rocks']

    def set_Texture(self,new_list):
        self._reload()
        self.physical['Texture']=new_list
        self.save_changes()
        self.__Texture=self.physical['Texture']

    def set_BD(self,new_list):
        self._reload()
        self.physical['BD']=new_list
        self.save_changes()
        self.__BD=self.physical['BD']

    def set_AirDry(self,new_list):
        self._reload()
        self.physical['AirDry']=new_list
        self.save_changes()
        self.__AirDry=self.physical['AirDry']

    def set_LL15(self,new_list):
        self._reload()
        self.physical['LL15']=new_list
        self.save_changes()
        self.__LL15=self.physical['LL15']

    def set_DUL(self,new_list):
        self._reload()
        self.physical['DUL']=new_list
        self.save_changes()
        self.__DUL=self.physical['DUL']

    def set_SAT(self,new_list):
        self._reload()
        self.physical['SAT']=new_list
        self.save_changes()
        self.__SAT=self.physical['SAT']

    def set_KS(self,new_list):
        self._reload()
        self.physical['KS']=new_list
        self.save_changes()
        self.__KS=self.physical['KS']

    
    # Getters
    def get_Thickness(self):
        return f'Depth (mm): {self.__Thickness}'
    def get_ParticleSizeSand(self):
        return f'Sand (%): {self.__ParticleSizeSand}'
    def get_ParticleSizeSilt(self):
        return f'Silt(%): {self.__ParticleSizeSilt}'
    def get_ParticleSizeClay(self):
        return f'Clay(%): {self.__ParticleSizeClay}'
    def get_Rocks(self):
        return f'Rocks(%): {self.__Rocks}'
    def get_Texture(self):
        return f'Texture: {self.__Texture}'
    def get_BD(self):
        return f'BD(g/cc): {self.__BD}'
    def get_AirDry(self):
        return f'AirDry(mm/mm): {self.__AirDry}'
    def get_LL15(self):
        return f'LL15(mm/mm): {self.__LL15}'
    def get_DUL(self):
        return f'DUL(mm/mm): {self.__DUL}'
    def get_SAT(self):
        return f'SAT(mm/mm): {self.__SAT}'
    def get_KS(self):
        return f'KS(mm/day): {self.__KS}'