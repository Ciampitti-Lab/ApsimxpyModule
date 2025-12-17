import geopandas as gpd
import apsimxpy
import numpy as np
import shutil
import pandas as pd
import glob
import os

folder = "/workspace/calibration/_2FieldSelection"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])



for id,row in fields.iterrows():
    shutil.copy(f"/workspace/calibration/_5RunSimulations/field_{row['id_GTD']}/CornSoybean_{row['id_GTD']}.apsimx",f"/workspace/CornSoybean.apsimx")
    init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='CornSoybean')
    sim1=apsimxpy.simulator(init_obj=init_obg)
    sim1.run()  
    results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
    results['Nitrogen']=row['NKg_Ha']
    results['id_GTD']=row['id_GTD']
    results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
    shutil.copy(f"/workspace/CornSoybean.Report.csv",f"/workspace/calibration/_5RunSimulations/field_{row['id_GTD']}/report_{row['id_GTD']}.csv")
    print("Simulations Finished for :",row['id_GTD'])

print("Simulations Finished , merging results... ")



lis_results=[]

for id,row in fields.iterrows():
    results=pd.read_csv(f"/workspace/calibration/_5RunSimulations/field_{row['id_GTD']}/report_{row['id_GTD']}.csv")
    results['Yield'] = (results['MaizeYield']+results['SoyBeanYield'])/1000
    results = results[results["Yield"] != 0]
    results = results[['Clock.Today','Yield','Nitrogen','id_GTD','MaizeYield','SoyBeanYield','ISoilWater.LeachNO3']]
    lis_results.append(results)
all_results = pd.concat(lis_results, ignore_index=True)
all_results.to_parquet("/workspace/calibration/_6EvaluationNotebooks/results.parquet", index=False)   

print("Results merged in a parquet!")
            