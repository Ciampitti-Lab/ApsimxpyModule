import geopandas as gpd
import pandas as pd
import shapely
import numpy as np
import contextlib
import glob
import os
import apsimxpy
from apsimxpy.field.soil.ssurgo import sdapoly, sdaprop
from apsimxpy.field.soil.ssurgo import soil_extraction as se
from apsimxpy.field.soil.ssurgo import saxton as sax
from apsimxpy.field.soil.ssurgo import soil_apsim as sa

# Importing fields and getting atitude and longitude 
folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])

fields = fields.to_crs(epsg=32616)

accurate_centroids = fields.centroid
centroids_geographic = accurate_centroids.to_crs(epsg=4326)

fields['long'] = round(centroids_geographic.x, 7)
fields['lat'] = round(centroids_geographic.y, 7)

# The apsimxpy module allows you to extract weather and soil properties
init_obg=apsimxpy.Initialize(apsim_folder_input='/workflow',apsim_file_input='CornSoybean')

# Set dates to extract weather variables
clock1=apsimxpy.Clock(init_obj=init_obg)
clock1.set_StartDate((1,1,1980)) 
clock1.set_EndDate((31,12,2024))

met=apsimxpy.Weather(init_obg)
soils=pd.DataFrame()
for idx, row in fields.iterrows():
    # Extraction of soil variables
    ssurgo_soil=se.get_poly_soil(row)
    main_soil=se.get_main_soil(ssurgo_soil)
    props=se.get_soil_props(ssurgo_soil,main_soil)
    s_apsim=sa.soil_apsim(props)
    s_apsim['id_cell']=row['id_cell']
    s_apsim['id_within_cell']=row['id_within_cell']
    print(s_apsim)
    soils = pd.concat([soils, s_apsim], ignore_index=True)
    # Extraction of weather variables
    lat = row['lat']
    long = row['long']
    filename = f"w_id_{row['id_cell']}_{row['id_within_cell']}"
    met.get_weather((round(long,7), round(lat,7)), clock1, filename)
    print(f'Weather and Soil Variables extracted for field {row['id_cell']}-{row['id_within_cell']}')

soils.to_csv("/workspace/soil/soils.csv",index_label=False)
print('Variables extracted successful!!! step 3/4')
