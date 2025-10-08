import json 
from ...utils import ApsimModifier

class Chemical(ApsimModifier):
    def __init__(self,init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        zone = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        # Find Soil
        soil = next(child for child in zone["Children"] if child["$type"] == "Models.Soils.Soil, Models")
        # Find CEC and pH
        chem = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Chemical, Models")
        # Find Solutes
        solutes = [child for child in soil["Children"] if child["$type"] == "Models.Soils.Solute, Models"]
        
        cec=chem['CEC']
        no3 = next(solute for solute in solutes if solute["Name"] == "NO3")
        nh4 = next(solute for solute in solutes if solute["Name"] == "NH4")
        urea = next(solute for solute in solutes if solute["Name"] == "Urea")
        # Pick Initial Values
        self.__cec=cec
        self.__NO3InitialValues=no3['InitialValues']
        self.__NH4InitialValues=nh4['InitialValues']
        self.__UreaInitialValues=urea['InitialValues']
        # Pick Layers
        self.__NO3Thickness=no3['Thickness']
        self.__NH4Thickness=nh4['Thickness']
        self.__UreaThickness=urea['Thickness']
        
        
        
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        # Find Zone
        zone = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        # Find Soil
        soil = next(child for child in zone["Children"] if child["$type"] == "Models.Soils.Soil, Models")
        # Find CEC and pH
        self.chem = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Chemical, Models")
        # Find Solutes
        self.solutes = [child for child in soil["Children"] if child["$type"] == "Models.Soils.Solute, Models"]
    
    def set_cec(self,new_list=None):
        self._reload()
        cec=self.chem['CEC']
        cec=new_list
        self.save_changes()
        self.__cec=cec
    
    def set_no3_initial_values(self,values=None):
        self._reload()
        no3 = next(solute for solute in self.solutes if solute["Name"] == "NO3")
        no3['InitialValues']=values
        self.save_changes()
        self.__NO3InitialValues=no3['InitialValues']

    def set_no3_thickness(self,layers=None):
        self._reload()
        no3 = next(solute for solute in self.solutes if solute["Name"] == "NO3")
        no3['Thickness']=layers
        self.save_changes()
        self.__NO3Thickness=no3['Thickness']
            
    def set_nh4_initial_values(self,values=None):
        self._reload()
        nh4 = next(solute for solute in self.solutes if solute["Name"] == "NH4")
        nh4['InitialValues']=values
        self.save_changes()
        self.__NH4InitialValues=nh4['InitialValues']

    def set_nh4_thickness(self,layers=None):
        self._reload()
        nh4 = next(solute for solute in self.solutes if solute["Name"] == "NH4")
        nh4['Thickness']=layers
        self.save_changes()
        self.__NH4Thickness=nh4['Thickness']
    
    def set_urea_initial_values(self,values=None):
        self._reload()
        urea = next(solute for solute in self.solutes if solute["Name"] == "Urea")
        urea['InitialValues']=values
        self.save_changes()
        self.__UreaInitialValues=urea['InitialValues']

        
    def set_urea_thickness(self,layers=None):
        self._reload()
        urea = next(solute for solute in self.solutes if solute["Name"] == "Urea")
        urea['Thickness']=layers
        self.save_changes()
        self.__UreaThickness=urea['Thickness']
        
    def get_no3(self):
        return self.__NO3InitialValues
    def get_nh4(self):
        return self.__NH4InitialValues
    def get_urea(self):
        return self.__UreaInitialValues
    def get_cec(self):
        return f'CEC:{self.__cec}'