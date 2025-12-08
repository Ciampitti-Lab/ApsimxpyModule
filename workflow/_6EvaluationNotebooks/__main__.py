import os
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import interact
import matplotlib.dates as mdates
from plotnine import *
import geopandas as gpd
import glob

##############################
# Simulations Visualizations #
##############################

### Folder Creation

folder_name_sim = "/workspace/workflow/_6EvaluationNotebooks/SimViz"

try:
    os.mkdir(folder_name_sim)
    print(f"Directory {folder_name_sim} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_sim} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Visualization Creation

#### Maize Yield Production
results = pd.read_parquet("/workspace/workflow/_6EvaluationNotebooks/results.parquet", engine="fastparquet")
results["Clock.Today"] = pd.to_datetime(results["Clock.Today"])

pivot_df_maize = results.pivot_table(
    index="Clock.Today",
    columns="Nitrogen",
    values='MaizeYield',
    aggfunc="max"
)

plt.figure(figsize=(12, 6))
for col in pivot_df_maize.columns:
    plt.plot(pivot_df_maize.index, pivot_df_maize[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_maize.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("Year")
plt.ylabel('MaizeYield')
plt.title("Maize yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/MaizeYield.jpeg")

#### SoyBean Production

pivot_df_soybean = results.pivot_table(
    index="Clock.Today",
    columns="Nitrogen",
    values='SoyBeanYield',
    aggfunc="max"
)
plt.figure(figsize=(12, 6))
for col in pivot_df_soybean.columns:
    plt.plot(pivot_df_soybean.index, pivot_df_soybean[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_soybean.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("Year")
plt.ylabel('SoyBeanYield')
plt.title("Soy Bean yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/SoyBeanYield.jpeg")

#### All Production

pivot_df_yield = results.pivot_table(
    index="Clock.Today",
    columns="Nitrogen",
    values='Yield',
    aggfunc="max"
)

plt.figure(figsize=(12, 6))
for col in pivot_df_yield.columns:
    plt.plot(pivot_df_yield.index, pivot_df_yield[col], label=f"Nitrogen {col}")

years = pd.DatetimeIndex(pivot_df_yield.index).year.unique()
plt.xticks(pd.to_datetime([f'{year}-01-01' for year in years]), years, rotation=45)

plt.xlabel("Year")
plt.ylabel('Yield')
plt.title("Yield over time")
plt.legend(title="Simulation", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("/workspace/workflow/_6EvaluationNotebooks/SimViz/Yield.jpeg")

############################
# Ground Truth Data Folder #
############################

folder_name_gt = "/workspace/workflow/_6EvaluationNotebooks/GTViz"

try:
    os.mkdir(folder_name_gt)
    print(f"Directory {folder_name_gt} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_gt} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Ground Truth Visualizations
GTD=pd.read_csv("/workspace/workflow/_6EvaluationNotebooks/GTD.csv")

#### Yield per region
YieldperRegion=(
    ggplot(GTD, aes(x='NKg_Ha', y='yield_ton', color='region')) +
    geom_point(size=1) +
    geom_smooth(method='lm',se=False) +
    theme_bw() +
    labs(
        x='Total Nitrogen (kg/ha)',
        y='Yield (t/ha)',
        color='County'
    )
)
YieldperRegion.save("/workspace/workflow/_6EvaluationNotebooks/GTViz/YieldperRegion.jpeg")

#### Boxplot Yield per region
YieldBoxRegion = (
    ggplot(GTD, aes(x='region', y='yield_ton', fill="region")) +
    geom_violin(alpha=0.6) +
    geom_boxplot(width=0.35) +
    theme_bw() +
    labs(
        x='County',
        y='Yield (t/ha)',
        fill='Source'
    )+
    theme(
        axis_text_x=element_text(size=8, angle=45, hjust=1),  
        figure_size=(12, 6)  
    )
)
YieldBoxRegion.save("/workspace/workflow/_6EvaluationNotebooks/GTViz/YieldBoxRegion")

# Ground Truth Data Folder

folder_name_gtsim = "/workspace/workflow/_6EvaluationNotebooks/SimGTViz"

try:
    os.mkdir(folder_name_gtsim)
    print(f"Directory {folder_name_gtsim} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_gtsim} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

#############################
# GTD vs SIM visualizations #
#############################

# Loading fields 
folder = "/workspace/workflow/_3AgroDataExtraction"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])
fields_region=fields[['id_cell','id_within_cell','region']]
fields_region_indexed = fields_region.set_index(['id_cell', 'id_within_cell'])

# Preparing Simulations
results['Year'] = results['Clock.Today'].dt.year
idx = results.groupby(['id_cell', 'Nitrogen','Year'])['Yield'].idxmax()
results = results.loc[idx].reset_index(drop=True)

## Selecting important variables
results = results[['id_cell','id_within_cell','Nitrogen','Yield','Year','MaizeYield']]

results_region = results.join(fields_region_indexed, on=['id_cell', 'id_within_cell'])

mask_c= (results_region['region'] == 'C') & (results_region['Year'] < 2014)
## Deleting years 2019 and 2020 (No have GTD for these years)

mask_other= (results_region['region'] != 'C') & (results_region['Year'] < 2019)

results_region_filtered_c= results_region[mask_c]
results_region_filtered_other= results_region[mask_other]

results_region_filtered=results_region_filtered_c.merge(results_region_filtered_other,how='outer')

# Selecting only the years where corn was produced
results_region_filtered=results_region_filtered[results_region_filtered['MaizeYield']!=0]

## SPLITING BY RANGES OF NITROGEN RATES
sim0=results_region_filtered[(results_region_filtered['Nitrogen']==0)]
sim100=results_region_filtered[(results_region_filtered['Nitrogen']==100)]
sim200=results_region_filtered[(results_region_filtered['Nitrogen']==200)]
sim300=results_region_filtered[(results_region_filtered['Nitrogen']==300)]

# Preparing Ground Truth
mask_GTD=(GTD['year'] < 2019) 
GTD_filtered = GTD[mask_GTD]
GTD_filtered['Yield'] = GTD_filtered['yield_ton']  
## SPLITING BY RANGES OF NITROGEN RATES
real0=GTD_filtered[GTD_filtered['NKg_Ha']==0]
real100=GTD_filtered[GTD_filtered['NKg_Ha']==100]
real200=GTD_filtered[GTD_filtered['NKg_Ha']==200]
real300=GTD_filtered[GTD_filtered['NKg_Ha']==300]

# Function to prepare data for a given rate
def prep_data(real, sim, rate):
    real_df = real.copy()
    real_df['Source'] = 'Ground Truth'
    real_df['Rate'] = f'{rate} KgN/Ha'
    
    sim_df = sim.copy()
    sim_df['Source'] = 'Simulated'
    sim_df['Rate'] = f'{rate} KgN/Ha'
    
    return pd.concat([real_df, sim_df], axis=0)

# Build one single dataframe with all rates
plot_data = pd.concat([
    prep_data(real0,   sim0,   0),
    prep_data(real100, sim100, 100),
    prep_data(real200, sim200, 200),
    prep_data(real300, sim300, 300)
])

boxplotComparation = (
    ggplot(plot_data, aes(x='region', y='Yield', fill='Source')) +
    geom_boxplot(position=position_dodge(width=0.8), width=0.3, alpha=0.6) +
    facet_wrap('~Rate', ncol=2, scales='free_y') +
    theme_bw() +
    labs(
        title='Ground Truth vs Simulated Yield',
        x='Region',
        y='Yield (t/ha)',
        fill='Data'
    ) +
    theme(
        axis_text_x=element_text(size=8, angle=45, hjust=1),
        figure_size=(12, 7)
    )
)

boxplotComparation.save("/workspace/workflow/_6EvaluationNotebooks/SimGTViz/boxplotComparation.jpeg")

## Paper visualizations

folder_name_paper = "/workspace/workflow/_6EvaluationNotebooks/PaperViz"

try:
    os.mkdir(folder_name_paper)
    print(f"Directory {folder_name_paper} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_paper} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Boxplot

plot_data = pd.concat([
    prep_data(results_region_filtered, GTD_filtered,   0)
])

plot_data.reset_index(drop=True,inplace=True)
boxplot_paper=(ggplot(plot_data ,aes(y='Yield',x='region',fill='region'))+
      geom_boxplot()+
      facet_wrap('Source')+
      theme_bw()+
      xlab('Region')+
      ylab('Yield (Ton/Ha)')+
      theme(legend_position='none'))

boxplot_paper.save("/workspace/workflow/_6EvaluationNotebooks/PaperViz/boxplotPaper.jpeg")

