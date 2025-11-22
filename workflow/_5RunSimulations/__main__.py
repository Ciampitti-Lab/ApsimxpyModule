import geopandas as gpd
import apsimxpy
import numpy as np
import shutil
import pandas as pd
import glob
import os

folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])

for id,row in fields.iterrows():
    if row['id_within_cell']%2==0:
        shutil.copy(f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/SoybeanCorn_{row['id_cell']}_{row['id_within_cell']}.apsimx",f"/workspace/SoybeanCorn.apsimx")
        
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='SoybeanCorn')
        
        fert=apsimxpy.field.management.Fertilize(init_obg)
        sim1=apsimxpy.simulator(init_obj=init_obg)
        
        clock1=apsimxpy.Clock(init_obj=init_obg)
        
        clock1.set_StartDate((1,1,2021)) 
        clock1.set_EndDate((31,12,2023))
        
        for n_rate in [20,150,270]:
            fert.set_fert_sowing(n_rate)
            sim1.run()
            results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            results['id_cell']=row['id_cell']
            results['id_within_cell']=row['id_within_cell']
            results['Nitrogen']=n_rate
            results['county']=row['countyname']
            results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            shutil.copy(f"/workspace/SoybeanCorn.Report.csv",f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv")
    else:
        shutil.copy(f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/CornSoybean_{row['id_cell']}_{row['id_within_cell']}.apsimx",f"/workspace/CornSoybean.apsimx")
        
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='CornSoybean')
        
        fert=apsimxpy.field.management.Fertilize(init_obg)
        sim1=apsimxpy.simulator(init_obj=init_obg)
        
        clock1=apsimxpy.Clock(init_obj=init_obg)
        
        clock1.set_StartDate((1,1,2021)) 
        clock1.set_EndDate((31,12,2024))
        
        for n_rate in np.arange(0, 301, 100):
            fert.set_fert_sowing(n_rate)
            sim1.run()
            results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            results['id_cell']=row['id_cell']
            results['id_within_cell']=row['id_within_cell']
            results['Nitrogen']=n_rate
            results['county']=row['countyname']
            results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            shutil.copy(f"/workspace/CornSoybean.Report.csv",f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv")

print("Simulations Finished , merging results... ")

lis_results=[]

for id,row in fields.iterrows():
    for dosis in np.arange(0, 301, 100):
        results=pd.read_csv(f"/workspace/workflow/_5RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{dosis}.csv")
        lis_results.append(results)
    all_results = pd.concat(lis_results, ignore_index=True)
    all_results.to_parquet("/workspace/workflow/_6EvaluationNotebooks/results.parquet", index=False)   

print("Results merged in a parquet!")
            