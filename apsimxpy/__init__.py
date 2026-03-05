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
                
        final = pd.concat(lis_df, ignore_index=True)
        final.to_parquet("/workspace/merged_results.parquet", index=False)
        self.apsim_file_input=self.apsim_file_input_original
        self.command[8]=f"/folder/{self.apsim_file_input}.apsimx"
        

# apsim-docker % docker run -it  -v "$(pwd):/workspace"  -v /var/run/docker.sock:/var/run/docker.sock  apsimxpy
