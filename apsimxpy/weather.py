import datetime
import pydaymet as daymet
from .utils import ApsimModifier
import os
import json 
import pandas as pd

class Weather(ApsimModifier):
    def __init__(self,init_obj):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
        # Model location in .apsimx 
        self.model_index=[(num,child) for num,child in enumerate(self.modifier['Children'][0]['Children']) if child["$type"]=="Models.Climate.Weather, Models"]
        self.model=self.model_index[0][0]
    def _reload(self):
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.modifier=json.loads(apsim_json)
    #To change the files
    def save_changes(self):
        with open(f"/workspace/{self.apsim_file_input}.apsimx", "w") as f:
            json.dump(self.modifier, f, indent=4)  
    
    # To get the weather from daymet
    def get_weather(self,coords,clock_object,filename): # latlong should be a tuple
        filename=filename+'.met'
        vars = ["prcp", "tmin", "tmax", "vp", "swe", "dayl", "srad"]
        dates=(clock_object.get_StartDate(),clock_object.get_EndDate())
        # Download data
        dmet = daymet.get_bycoords(coords, dates, variables=vars, time_scale="daily")
        
        all_dates = pd.date_range(start=dates[0], end=dates[1], freq='D')
        dmet = dmet.reindex(all_dates)
        dmet = dmet.interpolate(method='linear').ffill().bfill()
        # Adding columns of year and day
        dmet['day'] = dmet.index.dayofyear
        dmet['year'] = dmet.index.year
        #Filter dates and rest index
        dmet = dmet.reset_index()
        #Droping no needed columns
        dmet = dmet.drop(columns=['index', 'dayl (s)'])
        # Rename columns
        dmet.columns = ["rain", "radn", "swe", "maxt", "mint", "vp", "day", "year"]
        # Reorder columns
        dmet = dmet[["year", "day", "radn", "maxt", "mint", "rain", "vp", "swe"]]
        #W/m² to MJ/m²/day
        dmet['radn']=dmet["radn"] * 0.0864
        # TAV
        tav = dmet[["maxt", "mint"]].mean().mean()
        # AMP
        monthly_means = (dmet.groupby(dmet["day"] // 30)[["maxt", "mint"]]
                        .mean()
                        .mean(axis=1))
        amp = monthly_means.max() - monthly_means.min()
        filename = os.path.join("/workspace","weather", f"{filename}")
        
        # load the file to the weather folder
        with open(filename, "w") as f:
            f.write("!Title = Example Weather File\n")
            f.write("[weather.met.weather]\n")
            f.write(f"Latitude={coords[1]:.2f}\n")
            f.write(f"Longitude={coords[0]:.2f}\n")
            f.write(f"tav = {tav:.2f} (oC)\n")
            f.write(f"amp = {amp:.2f} (oC)\n\n")
            f.write("year day radn maxt mint rain vp swe\n")
            f.write("()   () (MJ/m2/day) (oC) (oC) (mm) (Pa) (mm)\n")
            dmet.to_csv(
                f,
                sep=" ",    
                index=False,
                header=False,
                float_format="%.2f",
                lineterminator="\n"
            )
        print(f'.met file created succesfully: {filename}')
    
    # To set the weather
    def set_weather(self,Filename):
        self._reload()
        Filename=f'/folder/weather/{Filename}.met'
        self.modifier['Children'][0]['Children'][self.model]['FileName']=Filename
        self.save_changes()