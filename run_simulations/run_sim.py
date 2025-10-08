import geopandas as gpd
import pandas as pd
import apsimxpy
import os

gdf=gpd.read_file("/workspace/SampleIndianaPolygons.geojson")
sample_gdf=gdf.sample(n=10,random_state=42)
sample_gdf=sample_gdf.reset_index()
gdf.shape

init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/CiampittiLab/APSIM/Python_Version/ApsimxpyModule',apsim_file_input='Module')

clock1=apsimxpy.Clock(init_obj=init_obg)

clock1.set_StartDate((1,1,1995)) 
clock1.set_EndDate((1,6,1995))

clock1.get_StartDate()
clock1.get_EndDate()


met=apsimxpy.Weather(init_obg)
soil1=apsimxpy.field.Soil(init_obg)
sim1=apsimxpy.simulator(init_obj=init_obg)

lis_df=[]
for idx,lat in enumerate(sample_gdf['lat'].unique()):
    long=sample_gdf['long'][idx]
    
    filename=f"w_{lat}_{long}"
    
    met.get_weather((long, lat),clock1,filename)
    soil1.set_Soil(latlon=(lat,long))
    met.set_weather(filename)
    
    sim1.run()
    os.remove(f'/workspace/weather/{filename}.met')
        
    # Soil 
    
    df=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
    df['n_sim']=idx
    lis_df.append(df)
    
final = pd.concat(lis_df, ignore_index=True)
final.to_parquet("/workspace/merged_results.parquet", index=False)    