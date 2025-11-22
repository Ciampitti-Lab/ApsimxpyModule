import geopandas as gpd
import pandas as pd
import apsimxpy
import os
import numpy as np
import shutil
import glob
import os

folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])

soils=pd.read_csv("/workspace/soil/soils.csv")
cols = ['SAND', 'CLAY', 'SILT', 'BD']
soils = soils[~(soils[cols].fillna(0) == 0).all(axis=1)]

lis_df=[]
count=0
for id,row in fields.iterrows():
    if row['id_within_cell']%2==0:
        
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='SoybeanCorn')

        clock1=apsimxpy.Clock(init_obj=init_obg)

        clock1.set_StartDate((1,1,2021)) 
        clock1.set_EndDate((31,12,2024))
        
        met=apsimxpy.Weather(init_obg)
        soil1=apsimxpy.field.Soil(init_obg)
        
        # Creating a folder for each field
        os.makedirs(f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}")
        # Setting the weather
        weather_name=f"w_id_{row['id_cell']}_{row['id_within_cell']}"
        met.set_weather(weather_name)
        # Setting soil
        soil=soils[(soils['id_cell']==row['id_cell']) & (soils['id_within_cell']==row['id_within_cell'])]
        soil1.set_soil_saxton(soil)
        # Saving file in folder
        shutil.copy("/workspace/CornSoybean.apsimx",f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/SoybeanCorn_{row['id_cell']}_{row['id_within_cell']}.apsimx")
        # Counting simulations
        count+=1
    else:
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='CornSoybean')

        clock1=apsimxpy.Clock(init_obj=init_obg)

        clock1.set_StartDate((1,1,2021)) 
        clock1.set_EndDate((31,12,2024))
        
        met=apsimxpy.Weather(init_obg)
        soil1=apsimxpy.field.Soil(init_obg)
        
        # Creating a folder for each field
        os.makedirs(f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}")
        # Setting the weather
        weather_name=f"w_id_{row['id_cell']}_{row['id_within_cell']}"
        met.set_weather(weather_name)
        # Setting soil
        soil=soils[(soils['id_cell']==row['id_cell']) & (soils['id_within_cell']==row['id_within_cell'])]
        soil1.set_soil_saxton(soil)
        # Saving file in folder
        shutil.copy("/workspace/SoybeanCorn.apsimx",f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/CornSoybean_{row['id_cell']}_{row['id_within_cell']}.apsimx")
        # Counting simulations
        count+=1
        
    
print(f'Preproccesing completed!!! Step 4/4 Now you can run simulations in APSIM')

