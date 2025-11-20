import geopandas as gpd
import apsimxpy
import numpy as np
import shutil
import pandas as pd

fields=gpd.read_file('/workspace/workflow/3.AgroDataExtraction/field_final_sample.geojson')
for id,row in fields.iloc[0:10,:].iterrows():
    if row['id_within_cell']%2==0:
        shutil.copy(f"/workspace/workflow/5.RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/SoybeanCorn_{row['id_cell']}_{row['id_within_cell']}.apsimx",f"/workspace/SoybeanCorn.apsimx")
        
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='SoybeanCorn')
        
        fert=apsimxpy.field.management.Fertilize(init_obg)
        sim1=apsimxpy.simulator(init_obj=init_obg)
        
        for n_rate in np.arange(0, 301, 100):
            fert.set_fert_sowing(n_rate)
            sim1.run()
            results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            results['id_cell']=row['id_cell']
            results['id_within_cell']=row['id_within_cell']
            results['Nitrogen']=n_rate
            results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            shutil.copy(f"/workspace/SoybeanCorn.Report.csv",f"/workspace/workflow/5.RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv")
    else:
        shutil.copy(f"/workspace/workflow/5.RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/CornSoybean_{row['id_cell']}_{row['id_within_cell']}.apsimx",f"/workspace/CornSoybean.apsimx")
        
        init_obg=apsimxpy.Initialize(apsim_folder_input='/Users/jorgeandresjolahernandez/Desktop/ApsimxpyModule',apsim_file_input='CornSoybean')
        
        fert=apsimxpy.field.management.Fertilize(init_obg)
        sim1=apsimxpy.simulator(init_obj=init_obg)
        
        for n_rate in np.arange(0, 301, 100):
            fert.set_fert_sowing(n_rate)
            sim1.run()
            results=pd.read_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            results['id_cell']=row['id_cell']
            results['id_within_cell']=row['id_within_cell']
            results['Nitrogen']=n_rate
            results.to_csv(f'/workspace/{init_obg.apsim_file_input}.Report.csv')
            shutil.copy(f"/workspace/CornSoybean.Report.csv",f"/workspace/workflow/5.RunSimulations/field_{row['id_cell']}_{row['id_within_cell']}/report_{row['id_cell']}_{row['id_within_cell']}_N{n_rate}.csv")
            
            