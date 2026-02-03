import os
import subprocess
import shutil
import pandas as pd
from . import utils
from .clock import Clock
from .weather import Weather
from .field import Field
from .helptree import HelpTree
from .microclimate import MicroClimate



#############################################
# Object: Initialize the module functions #
#############################################
class Initialize:
    def __init__(self,apsim_folder_input,apsim_file_input):
        self.apsim_folder_input=apsim_folder_input
        self.apsim_file_input=apsim_file_input
##########################################################
# Object: Simulator to run one or multiple simulations #
##########################################################
class simulator:
    def __init__(self,init_obj=None):    
        self.apsim_folder_input=init_obj.apsim_folder_input
        self.apsim_file_input=init_obj.apsim_file_input
        self.apsim_file_input_original=init_obj.apsim_file_input
        # Command for run docker container
        self.command = [
            "docker", "run", "--rm", "--platform", "linux/amd64",
            "-v", f"{self.apsim_folder_input}:/folder",
            "apsiminitiative/apsimng",
            f"/folder/{self.apsim_file_input}.apsimx",
            "--csv"
        ]
        
    def run(self):
        try:
            result = subprocess.run(self.command, check=True, capture_output=True, text=True)
            print("Simulation successful!")
            if result.stderr!='':
                print("Warnings or Errors:\n", result.stderr)
            else: 
                pass
            
        except subprocess.CalledProcessError as e:
            print("Error running command:", e)
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            if e.stderr=='':
                print('File not found - load the correct name of the file')
    def run_multi(self,setter=None,values=None):
        if setter is not None and values is not None:
            lis_df=[]
            for sim,value in enumerate(values):
                setter(value) ## Here I change the value of the attribute-
                if sim==0:
                    self.run()
                    # Data recollected
                    df=pd.read_csv(f'/workspace/{self.apsim_file_input}.Report.csv')
                    df['n_sim']=sim
                    lis_df.append(df)
                    # Deleting last database created (.db)
                    os.remove(f'/workspace/{self.apsim_file_input}.db')
                    # Deleting last shared memory file (.db-shm)
                    os.remove(f'/workspace/{self.apsim_file_input}.db-shm')
                    # Deleting last Write-Ahead Log. (.db-wal)
                    os.remove(f'/workspace/{self.apsim_file_input}.db-wal')
                    # Deleting temporal csv. (.Report.csv)
                    os.remove(f'/workspace/{self.apsim_file_input}.Report.csv')
                    self.apsim_file_input=self.apsim_file_input + str(sim)
                else:
                    shutil.copy(f'/workspace/{self.apsim_file_input_original}.apsimx', f'/workspace/{self.apsim_file_input}.apsimx')
                    self.command[8]=f"/folder/{self.apsim_file_input}.apsimx"
                    self.run()
                    df=pd.read_csv(f'/workspace/{self.apsim_file_input}.Report.csv')
                    df['n_sim']=sim
                    lis_df.append(df)
                    self.apsim_file_input=self.apsim_file_input_original + str(sim)
                    print(self.apsim_file_input)
                    # Deleting last simulation file (.apsimx)
                    os.remove(f'/workspace/{self.apsim_file_input_original + str(sim-1)}.apsimx')
                    # Deleting last database created (.db)
                    os.remove(f'/workspace/{self.apsim_file_input_original + str(sim-1)}.db')
                    # Deleting last shared memory file (.db-shm)
                    os.remove(f'/workspace/{self.apsim_file_input_original + str(sim-1)}.db-shm')
                    # Deleting last Write-Ahead Log. (.db-wal)
                    os.remove(f'/workspace/{self.apsim_file_input_original + str(sim-1)}.db-wal')
                    # Deleting temporal csv. (.Report.csv)
                    os.remove(f'/workspace/{self.apsim_file_input_original + str(sim-1)}.Report.csv')
                
        final = pd.concat(lis_df, ignore_index=True)
        final.to_parquet("/workspace/merged_results.parquet", index=False)
        self.apsim_file_input=self.apsim_file_input_original
        self.command[8]=f"/folder/{self.apsim_file_input}.apsimx"
        

# apsim-docker % docker run -it  -v "$(pwd):/workspace"  -v /var/run/docker.sock:/var/run/docker.sock  apsimxpy