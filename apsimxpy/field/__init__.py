import json 
from ..utils import ApsimModifier
from .surfaceorganicmatter import SOM
from .soil import Soil
#########################################
############# Object: Field #############
#########################################

class Field(ApsimModifier):
    # PARAMETERS OF THE MODEL FIELD
    def __init__(self,init_obj=None,Area=1,Slope=0,AspectAngle=0,Altitude=50):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        # Model location in .apsimx 
        model_index=[(num,child) for num,child in enumerate(self.modifier['Children'][0]['Children']) if child["$type"]=="Models.Core.Zone, Models"]
        self.model=model_index[0][0]
        
        # Attributes location in .apsimx 
        self.__Area=Area
        self.modifier['Children'][0]['Children'][self.model]['Area']=Area
        self.__Slope=Slope
        self.modifier['Children'][0]['Children'][self.model]['Slope']=Slope
        self.__AspectAngle=AspectAngle
        self.modifier['Children'][0]['Children'][self.model]['AspectAngle']=AspectAngle
        self.__Altitude=Altitude
        self.modifier['Children'][0]['Children'][self.model]['Altitude']=Altitude
        self.save_changes()
    # To change the file
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
    
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Field attributes to get and set            
    
    def get_Area(self):
        return self.__Area
    
    def set_Area(self,new_Area):
        self._reload()
        self.modifier['Children'][0]['Children'][self.model]['Area']=new_Area
        self.save_changes()
        self.__Area=new_Area 
    
    def get_Slope(self):
        return self.__Slope
    
    def set_Slope(self,new_Slope):
        self._reload()
        self.modifier['Children'][0]['Children'][self.model]['Slope']=new_Slope
        self.save_changes()
        self.__Slope=new_Slope
    
    def get_AspectAngle(self):
        return self.__AspectAngle
    
    def set_AspectAngle(self,new_AspectAngle):
        self._reload()
        self.modifier['Children'][0]['Children'][self.model]['AspectAngle']=new_AspectAngle
        self.save_changes()
        self.__AspectAngle=new_AspectAngle
    
    def get_Altitude(self):
        return self.__Altitude
    
    def set_Altitude(self,new_Altitude):
        self._reload()
        self.modifier['Children'][0]['Children'][self.model]['Altitude']=new_Altitude
        self.save_changes()
        self.__Altitude=new_Altitude

    # Crop Selection
    def add_crop(self,NameCrop,ll,kl,xf):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.physical = next(prop for prop in soil['Children'] if prop["$type"] == "Models.Soils.Physical, Models")
        
        Thickness=self.physical['Thickness']
        if len(Thickness)==len(ll)==len(kl)==len(xf):
            new_crop_soil={
                    '$type': 'Models.Soils.SoilCrop, Models',
                    'LL': ll,
                    'KL': kl,
                    'XF': xf,
                    'LLMetadata': [None]*len(Thickness),
                    'KLMetadata': [None]*len(Thickness),
                    'XFMetadata': [None]*len(Thickness),
                    'Name': NameCrop+'Soil',
                    'ResourceName': None,
                    'Children': [],
                    'Enabled': True,
                    'ReadOnly': False
                }
            self.physical['Children'].append(new_crop_soil)
            print('New crop added successful')
        else:
            print('Error: Parameters needs to have the same length')
        self.save_changes() 