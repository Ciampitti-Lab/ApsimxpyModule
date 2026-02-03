import json 
from ...utils import ApsimModifier

class SoilWater(ApsimModifier):
    def __init__(self, init_obj):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        waterb = next(prop for prop in soil['Children'] if prop["$type"] == "Models.WaterModel.WaterBalance, Models")

        self.__SummerDate=waterb['SummerDate']
        self.__SummerU=waterb['SummerU']
        self.__SummerCona=waterb['SummerCona']
        self.__WinterDate=waterb['WinterDate']
        self.__WinterU=waterb['WinterU']
        self.__WinterCona=waterb['WinterCona']
        self.__DiffusConst=waterb['DiffusConst']
        self.__DiffusSlope=waterb['DiffusSlope']
        self.__Salb=waterb['Salb']
        self.__CN2Bare=waterb['CN2Bare']
        self.__CNRed=waterb['CNRed']
        self.__CNCov=waterb['CNCov']
        self.__DischargeWidth=waterb['DischargeWidth']
        self.__CatchmentArea=waterb['CatchmentArea']
        self.__PSIDul=waterb['PSIDul']
        self.__SWCON=waterb['SWCON']
        self.__KLAT=waterb['KLAT']
        
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        children = self.modifier["Children"][0]["Children"]
        zones = next(child for child in children if child["$type"] == "Models.Core.Zone, Models")
        soil = next(zone for zone in zones['Children'] if zone["$type"] == "Models.Soils.Soil, Models")
        self.waterb = next(prop for prop in soil['Children'] if prop["$type"] == "Models.WaterModel.WaterBalance, Models")
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    # Setters
    def set_SummerDate(self,new_value):
        self._reload()
        self.waterb['SummerDate']=new_value
        self.save_changes()
        self.__SummerDate=self.waterb['SummerDate']


    def set_SummerU(self,new_value):
        self._reload()
        self.waterb['SummerU']=new_value
        self.save_changes()
        self.__SummerU=self.waterb['SummerU']

    def set_SummerCona(self,new_value):
        self._reload()
        self.waterb['SummerCona']=new_value
        self.save_changes()
        self.__SummerCona=self.waterb['SummerCona']


    def set_WinterDate(self,new_value):
        self._reload()
        self.waterb['WinterDate']=new_value
        self.save_changes()
        self.__WinterDate=self.waterb['WinterDate']


    def set_WinterU(self,new_value):
        self._reload()
        self.waterb['WinterU']=new_value
        self.save_changes()
        self.__WinterU=self.waterb['WinterU']


    def set_WinterCona(self,new_value):
        self._reload()
        self.waterb['WinterCona']=new_value
        self.save_changes()
        self.__WinterCona=self.waterb['WinterCona']


    def set_DiffusConst(self,new_value):
        self._reload()
        self.waterb['DiffusConst']=new_value
        self.save_changes()
        self.__DiffusConst=self.waterb['DiffusConst']


    def set_DiffusSlope(self,new_value):
        self._reload()
        self.waterb['DiffusSlope']=new_value
        self.save_changes()
        self.__DiffusSlope=self.waterb['DiffusSlope']


    def set_Salb(self,new_value):
        self._reload()
        self.waterb['Salb']=new_value
        self.save_changes()
        self.__Salb=self.waterb['Salb']


    def set_CN2Bare(self,new_value):
        self._reload()
        self.waterb['CN2Bare']=new_value
        self.save_changes()
        self.__CN2Bare=self.waterb['CN2Bare']


    def set_CNRed(self,new_value):
        self._reload()
        self.waterb['CNRed']=new_value
        self.save_changes()
        self.__CNRed=self.waterb['CNRed']


    def set_CNCov(self,new_value):
        self._reload()
        self.waterb['CNCov']=new_value
        self.save_changes()
        self.__CNCov=self.waterb['CNCov']


    def set_DischargeWidth(self,new_value):
        self._reload()
        self.waterb['DischargeWidth']=new_value
        self.save_changes()
        self.__DischargeWidth=self.waterb['DischargeWidth']


    def set_CatchmentArea(self,new_value):
        self._reload()
        self.waterb['CatchmentArea']=new_value
        self.save_changes()
        self.__CatchmentArea=self.waterb['CatchmentArea']

    def set_PSIDul(self,new_value):
        self._reload()
        self.waterb['PSIDul']=new_value
        self.save_changes()
        self.__PSIDul=self.waterb['PSIDul']
            
    def set_SWCON(self,new_value):
        self._reload()
        self.waterb['SWCON']=new_value
        self.save_changes()
        self.__SWCON=self.waterb['SWCON']


    def set_KLAT(self,new_list):
        self._reload()
        self.waterb['KLAT']=new_list
        self.save_changes()
        self.__KLAT=self.waterb['KLAT']
            
    #Getters
    def get_SummerDate(self):
        return f'Start Date for switch to summer parameters for soil water evaporation (dd-mmm): {self.__SummerDate}'

    def get_SummerU(self):
        return f'Cumulative soil water evaporation to reach the end of stage 1 soil water evaporation in winter (a.k.a U)(mm): {self.__SummerU}'

    def get_SummerCona(self):
        return f'Drying coefficient for stage 2 soil water evaporation in summer (a-k-a ConA): {self.__SummerCona}'

    def get_WinterDate(self):
        return f'Start date for switch to winter parameters for soil water evaporation in summer (a.k.a. U)(mm): {self.__WinterDate}'

    def get_WinterU(self):
        return f'Cummulative soil water evaporation to reach the end of stage 1 soil water evaporation in winter (a.k.a U)(mm): {self.__WinterU}'

    def get_WinterCona(self):
        return f'Drying coefficient for stage 2 soil water evaporation in winter (a.k.a ConA): {self.__WinterCona}'
 
    def get_DiffusConst(self):
        return f'Constant in the soil water diffusivity calculation (mm2/day): {self.__DiffusConst}'

    def get_DiffusSlope(self):
        return f'Effect of soil water storage above the lower limit on soil water diffusivity (mm): {self.__DiffusSlope}'

    def get_Salb(self):
        return f'Fraction of incoming radiation reflected from bare soil: {self.__Salb}'

    def get_CN2Bare(self):
        return f'Runoff Curve Number (CN) for bare soil with average moisture: {self.__CN2Bare}'
   
    def get_CNRed(self,new_value):
        return f'Max. Reduction in curve number due to a cover: {self.__CNRed}'
    
    def get_CNCov(self):
        return f'Cover for max curve number reduction: {self.__CNCov}'

    def get_DischargeWidth(self):
        return f'Basal width of the downslope boundary of the catchment for lateral flow calculation (m): {self.__DischargeWidth}'

    def get_CatchmentArea(self):
        return f'Catchment area for lateral flow calculations (m2):  {self.__CatchmentArea}'

    def get_PSIDul(self):
        return f'Matric Potential at DUL (cm):  {self.__PSIDul}'
            
    def get_SWCON(self):
        return f'SWCON (d): {self.__SWCON}'

    def get_KLAT(self):
        return f'KLAT (mm/d): {self.__KLAT}'