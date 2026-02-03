from datetime import datetime
import json 
from .utils import ApsimModifier

#########################################
############# Object A: Clock ###########
#########################################
class Clock(ApsimModifier):
    # PARAMETERS OF THE MODEL CLOCK
    def __init__(self,start=(1,1,1989),end=(31,12,1989),init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        
        # Model location in .apsimx 
        self.model_index=[(num,child) for num,child in enumerate(self.modifier['Children'][0]['Children']) if child["$type"]=="Models.Clock, Models"]
        self.model=self.model_index[0][0]
        
        # Establish values for start date
        splitDt_Start=datetime.fromisoformat(self.modifier['Children'][0]['Children'][self.model]['Start'])
        splitDt_Start = splitDt_Start.replace(
                            year=start[2],
                            month=start[1],
                            day=start[0]
                        )
        splitDt_Start = splitDt_Start.isoformat()
        self.modifier['Children'][0]['Children'][self.model]['Start']=splitDt_Start
        
        self.__StartDate=splitDt_Start
        
        # Establish values for end date
        splitDt_End=datetime.fromisoformat(self.modifier['Children'][0]['Children'][self.model]['End'])
        splitDt_End = splitDt_End.replace(
                            year=end[2],
                            month=end[1],
                            day=end[0]
                        )
        splitDt_End = splitDt_End.isoformat()
        self.modifier['Children'][0]['Children'][self.model]['End']=splitDt_End
        
        self.__EndDate=splitDt_End
        
        
        self.save_changes()
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
    #To change the files
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Clock attributes to get and set
    def get_StartDate(self):
        return self.__StartDate
    def set_StartDate(self,new_Start):
        self._reload()
        splitDt=datetime.fromisoformat(self.modifier['Children'][0]['Children'][self.model]['Start'])
        splitDt = splitDt.replace(
                            year=new_Start[2],
                            month=new_Start[1],
                            day=new_Start[0]
                        )
        dt_str_back = splitDt.isoformat()
        self.modifier['Children'][0]['Children'][self.model]['Start']=dt_str_back
        self.save_changes()
        self.__StartDate=dt_str_back
        
        
    def get_EndDate(self):
        return self.__EndDate
    def set_EndDate(self,new_End):
        self._reload()
        splitDt=datetime.fromisoformat(self.modifier['Children'][0]['Children'][self.model]['End'])
        splitDt = splitDt.replace(
                            year=new_End[2],
                            month=new_End[1],
                            day=new_End[0]
                        )
        dt_str_back = splitDt.isoformat()
        self.modifier['Children'][0]['Children'][self.model]['End']=dt_str_back
        self.save_changes()
        self.__EndDate=dt_str_back