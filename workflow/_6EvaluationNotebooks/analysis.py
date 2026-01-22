from scipy.interpolate import make_interp_spline
import geopandas as gpd
import pandas as pd
import numpy as np
import glob
import os

class results_config:
    def __init__(self, path_results):
        self.path_results=path_results
        
    def read_results(self):
        # Results
        self.results=pd.read_parquet(self.path_results, engine="fastparquet")
        self.results["Clock.Today"] = pd.to_datetime(self.results["Clock.Today"])
        
        # Loading fields 
        folder_fields = "/workspace/workflow/_3AgroDataExtraction"
        geojson_field = glob.glob(os.path.join(folder_fields, "*.geojson"))
        fields=gpd.read_file(geojson_field[0])
        fields_region=fields[['id_cell','id_within_cell','region']]
        self.fields_region= fields_region.set_index(['id_cell', 'id_within_cell'])
        
    def create_folders(self):
        
        # Simulations Visualizations Folder
        folder_name_sim = "/workspace/workflow/_6EvaluationNotebooks/SimViz"
        try:
            os.mkdir(folder_name_sim)
            print(f"Directory {folder_name_sim} created succesfully.")
        except FileExistsError:
            print(f"Directory {folder_name_sim} already exists. ")
        except Exception as e:
            print(f"An error occurred {e}")
            
        # Grund Truth Data visualizations Folder
        folder_name_gt = "/workspace/workflow/_6EvaluationNotebooks/GTViz"

        try:
            os.mkdir(folder_name_gt)
            print(f"Directory {folder_name_gt} created succesfully.")
        except FileExistsError:
            print(f"Directory {folder_name_gt} already exists. ")
        except Exception as e:
            print(f"An error occurred {e}")
            

        # GTD vs SIM visualizations Folder
        folder_name_gtsim = "/workspace/workflow/_6EvaluationNotebooks/SimGTViz"
        
        try:
            os.mkdir(folder_name_gtsim)
            print(f"Directory {folder_name_gtsim} created succesfully.")
        except FileExistsError:
            print(f"Directory {folder_name_gtsim} already exists. ")
        except Exception as e:
            print(f"An error occurred {e}")
            
        # Paper visualizations Folder
        folder_name_paper = "/workspace/workflow/_6EvaluationNotebooks/PaperViz"

        try:
            os.mkdir(folder_name_paper)
            print(f"Directory {folder_name_paper} created succesfully.")
        except FileExistsError:
            print(f"Directory {folder_name_paper} already exists. ")
        except Exception as e:
            print(f"An error occurred {e}")
                
        
    ##################################################################################################################################################
    # Simulations Visualizations #
    ##################################################################################################################################################
    def maize_yield_prod(self):
        # Select the max yield per day
        pivot_df_maize = self.results.pivot_table(
            index="Clock.Today",
            columns="Nitrogen",
            values='MaizeYield',
            aggfunc="max"
        )
        return pivot_df_maize
    def soybean_yield_prod(self):
         # Select the max yield per day
        pivot_df_soybean = self.results.pivot_table(
            index="Clock.Today",
            columns="Nitrogen",
            values='SoyBeanYield',
            aggfunc="max"
        )
        return pivot_df_soybean
    def all_yield_prod(self):
         # Select the max yield per day
        pivot_df_yield = self.results.pivot_table(
            index="Clock.Today",
            columns="Nitrogen",
            values='Yield',
            aggfunc="max"
        )
        return pivot_df_yield
    ################################################################################################################################################
    # Ground Truth Data Folder #
    ################################################################################################################################################
    def read_gtd(self):
        self.gtd=pd.read_csv("/workspace/workflow/_6EvaluationNotebooks/GTD.csv")
        mask_GTD=(self.gtd['year'] < 2019) 
        self.gtd = self.gtd[mask_GTD]
        return self.gtd
    #################################################################################################################################################
    # GTD vs SIM visualizations #
    #################################################################################################################################################
    def results_prepare(self):
        self.results['Year'] = self.results['Clock.Today'].dt.year
        # Selecting the best yield per year
        idx = self.results.groupby(['id_cell', 'Nitrogen','Year'])['Yield'].idxmax()
        self.results = self.results.loc[idx].reset_index(drop=True)
        ## Selecting important variables
        self.results = self.results[['id_cell','id_within_cell','Nitrogen','Yield','Year','MaizeYield']]
        # Results df takes region from fields_region
        results_region = self.results.join(self.fields_region, on=['id_cell', 'id_within_cell'])
        
        
        # Only GTD for region C before 2015, and no data for 2009
        mask_c= (results_region['region'] == 'C') & (results_region['Year'] <= 2014) & (results_region['Year']!=2009)
        # No GTD for 2019 and 2020 for region NC 
        mask_nc= (results_region['region'] == 'NC') & (~results_region['Year'].isin([2019, 2020]))
        # No GTD for 2016, 2017, 2018, 2019 and 2020 for region NE 
        mask_ne= (results_region['region'] == 'NE') & (~results_region['Year'].isin([2016,2017,2018,2019, 2020]))
        
        results_c= results_region[mask_c]
        results_nc= results_region[mask_nc]
        results_ne= results_region[mask_ne]
        
        # Results Filtered
        results_all_region = (
            results_c
            .merge(results_nc, how='outer')
            .merge(results_ne, how='outer')
        )
        
        # Selecting only the years where corn was produced
        self.results_all_region=results_all_region[results_all_region['MaizeYield']!=0]
    
    def boxplot_nrate_config(self):
        ## SPLITING BY RANGES OF NITROGEN RATES
        sim0=self.results_all_region[(self.results_all_region['Nitrogen']==0)]
        sim100=self.results_all_region[(self.results_all_region['Nitrogen']==100)]
        sim200=self.results_all_region[(self.results_all_region['Nitrogen']==200)]
        sim300=self.results_all_region[(self.results_all_region['Nitrogen']==300)]
        
        truth0=self.gtd[self.gtd['Nitrogen']==0]
        truth100=self.gtd[self.gtd['Nitrogen']==100]
        truth200=self.gtd[self.gtd['Nitrogen']==200]
        truth300=self.gtd[self.gtd['Nitrogen']==300]
        
        def prep_data(real, sim, rate):
            real_df = real.copy()
            real_df['Source'] = 'Ground Truth'
            real_df['Rate'] = f'{rate} KgN/Ha'
            
            sim_df = sim.copy()
            sim_df['Source'] = 'Simulated'
            sim_df['Rate'] = f'{rate} KgN/Ha'
            
            return pd.concat([real_df, sim_df], axis=0)

        # Build one single dataframe with all rates
        boxplot_data = pd.concat([
            prep_data(truth0,   sim0,   0),
            prep_data(truth100, sim100, 100),
            prep_data(truth200, sim200, 200),
            prep_data(truth300, sim300, 300)
        ])
        return boxplot_data
    #################################################################################################################################################
    # Paper visualizations #
    #################################################################################################################################################    
    
    # AONR (Agronomic Optimum Nitrogen Rate)
    def average_aonr(self,fit=True):
        sim=self.results_all_region[['Nitrogen','Yield','region']]
        truth=self.gtd[['Nitrogen','Yield','region']]
        
        # Adding label real/simulations
        sim['Source']='Simulated'
        truth['Source']='Ground Truth'
        
        # Merging
        sim_truth=pd.concat([truth,sim])
        
        # average curve per region (6 curves)
        real_sim_avg = (sim_truth.groupby(['Nitrogen','region','Source'])['Yield'].mean().reset_index())
        
        # Getting percentage maximum yield
        real_sim_avg['yield_por'] = (
            real_sim_avg['Yield'] /
            real_sim_avg.groupby(['region','Source'])['Yield'].transform('max') * 100
        )
        
        # Creating the curves
        curves = []

        if fit==True:
            for (region, source), d in real_sim_avg.groupby(['region','Source']):
                d = d.sort_values("Nitrogen")
                x = d["Nitrogen"].values
                y = d["yield_por"].values
                xs = np.linspace(x.min(), x.max(), 100)
                spline = make_interp_spline(x, y, k=2)
                ys = spline(xs)
                ys = np.clip(ys, 0, 100)
                
                curves.append(pd.DataFrame({
                    "Nitrogen": xs,
                    "yield_por": ys,
                    "region": region,
                    "Source": source
                }))
            curves_df = pd.concat(curves, ignore_index=True)
        else:
            curves_df = real_sim_avg
        
        return curves_df
    
    def aonr_calculate(self):
        # AONR Simulations
        sim=self.results_all_region
        idx_max_yield_sim=sim.groupby(['id_cell','id_within_cell','Year'])['Yield'].idxmax()
        max_yield_df_sim = sim.loc[idx_max_yield_sim, ['id_cell','id_within_cell','Year','region', 'Nitrogen']]
        
        ## Counting all the aonrs per regions and nitrogen rate
        sim_counts = (
            max_yield_df_sim
            .groupby(['region', 'Nitrogen'])
            .size()   
            .reset_index(name='count')  
        )
        sim_counts['Source']='Simulated'
        
        
        # AONR Ground Truth Data
        truth=self.gtd
        truth['id_truth']=np.arange(len(truth))//13 # 7 is the number of rates of nitrogen to group the rows (They are sorted)
        idx_max_yield_truth=truth.groupby('id_truth')['Yield'].idxmax()
        max_yield_df_truth = truth.loc[idx_max_yield_truth, ['id_truth', 'Nitrogen','region']].set_index('id_truth')
        
        ## Counting all the aonrs per regions
        truth_counts = (
            max_yield_df_truth
            .groupby(['region', 'Nitrogen'])
            .size()   
            .reset_index(name='count')  
        )
        truth_counts['Source']='truth'
        
        # Merging counts
        total_counts=pd.concat([sim_counts,truth_counts])
        totals = total_counts.groupby(['Source','region'])['count'].transform('sum')
        total_counts['percentaje']=total_counts['count'] / totals *100
        print(total_counts)
        return total_counts
        
        
    
    
    

