import os
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import interact
import matplotlib.dates as mdates
from plotnine import *
import geopandas as gpd
import glob
import numpy as np
from scipy.interpolate import make_interp_spline

##############################
# Simulations Visualizations #
##############################

### Folder Creation

folder_name_sim = "/workspace/calibration/_6EvaluationNotebooks/SimViz"

try:
    os.mkdir(folder_name_sim)
    print(f"Directory {folder_name_sim} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_sim} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Visualization Creation

#### Maize Yield Production
results = pd.read_parquet("/workspace/calibration/_6EvaluationNotebooks/results.parquet", engine="fastparquet")
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
plt.savefig("/workspace/calibration/_6EvaluationNotebooks/SimViz/MaizeYield.jpeg")

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
plt.savefig("/workspace/calibration/_6EvaluationNotebooks/SimViz/SoyBeanYield.jpeg")

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
plt.savefig("/workspace/calibration/_6EvaluationNotebooks/SimViz/Yield.jpeg")

############################
# Ground Truth Data Folder #
############################

folder_name_gt = "/workspace/calibration/_6EvaluationNotebooks/GTViz"

try:
    os.mkdir(folder_name_gt)
    print(f"Directory {folder_name_gt} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_gt} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Ground Truth Visualizations
GTD=pd.read_csv("/workspace/calibration/_1GTDtransform/GTDtransform.csv")

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
YieldperRegion.save("/workspace/calibration/_6EvaluationNotebooks/GTViz/YieldperRegion.jpeg")

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
YieldBoxRegion.save("/workspace/calibration/_6EvaluationNotebooks/GTViz/YieldBoxRegion")

# Ground Truth Data Folder

folder_name_gtsim = "/workspace/calibration/_6EvaluationNotebooks/SimGTViz"

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
folder = "/workspace/calibration/_2FieldSelection"
geojson_file = glob.glob(os.path.join(folder, "*.geojson"))
fields=gpd.read_file(geojson_file[0])
fields_region=fields[['id_GTD','region']]
fields_region_indexed = fields_region.set_index(['id_GTD'])

# Preparing Simulations
results['Year'] = results['Clock.Today'].dt.year
idx = results.groupby(['id_GTD', 'Nitrogen','Year'])['Yield'].idxmax()
results = results.loc[idx].reset_index(drop=True)

## Selecting important variables
results = results[['id_GTD','Nitrogen','Yield','Year','MaizeYield']]

results_region = results.join(fields_region_indexed, on=['id_GTD'])

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

boxplotComparation.save("/workspace/calibration/_6EvaluationNotebooks/SimGTViz/boxplotComparation.jpeg")

all_data=pd.merge(results_region_filtered,GTD_filtered,on='id_GTD',how='inner')

rmse=round(np.sqrt(np.mean((all_data['Yield_y']-all_data['Yield_x'])**2)),2)

scatterComparation = (
    ggplot(all_data, aes(x='Yield_x', y='Yield_y')) +
    geom_point(alpha=0.5) + 
    geom_smooth(method='lm', color='red') + 
    #facet_wrap('~region_x') +
    labs(x='Simulated',y='Ground Truth Data',title=f'RMSE: {rmse}')+
    theme_minimal()
)
scatterComparation.save("/workspace/calibration/_6EvaluationNotebooks/SimGTViz/scatterComparation.jpeg")
##########################
## Paper visualizations ##
##########################
folder_name_paper = "/workspace/calibration/_6EvaluationNotebooks/PaperViz"

try:
    os.mkdir(folder_name_paper)
    print(f"Directory {folder_name_paper} created succesfully.")
except FileExistsError:
    print(f"Directory {folder_name_paper} already exists. ")
except Exception as e:
    print(f"An error occurred {e}")

### Boxplot


plot_data.reset_index(drop=True,inplace=True)
boxplot_paper=(ggplot(plot_data ,aes(y='Yield',x='region',fill='region'))+
      geom_boxplot()+
      facet_wrap('~Source')+
      theme_bw()+
      xlab('Region')+
      ylab('Yield (Ton/Ha)')+
      theme(legend_position='none'))

boxplot_paper.save("/workspace/calibration/_6EvaluationNotebooks/PaperViz/boxplotPaper.jpeg")

### Curves 

# Selecting variables to do the merge
sim_results=results_region_filtered[['Nitrogen','Yield','region']]

real_results=GTD_filtered[['NKg_Ha','yield_ton','region']]
real_results.rename(columns={'NKg_Ha':'Nitrogen','yield_ton':'Yield'},inplace=True)

# Adding label real/simulations
sim_results['Source']='Simulated'
real_results['Source']='Ground Truth'

# Merging
real_sim_results=pd.concat([real_results,sim_results])

# Getting average Yield
real_sim_mean = (real_sim_results.groupby(['Nitrogen','region','Source'])['Yield'].mean().reset_index())
real_sim_mean['Yield']=real_sim_mean['Yield']

# Getting percentage maximum yield
real_sim_mean['yield_por'] = (
    real_sim_mean['Yield'] /
    real_sim_mean.groupby(['region','Source'])['Yield'].transform('max') * 100
)

# Creating the curves
curves = []

for (region, source), d in real_sim_mean.groupby(['region','Source']):
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

curves_df= pd.concat(curves, ignore_index=True)

curvesPaper = (
    ggplot()
    + geom_line(curves_df, aes("Nitrogen", "yield_por", color="region"), size=3)
    + theme_bw()
    + labs(
        x="N rate (Kg/Ha)",
        y="Percent of maximum yield",
        color="Region"
    )
    + facet_wrap("Source")
)
curvesPaper.save("/workspace/calibration/_6EvaluationNotebooks/PaperViz/curvesPaper.jpeg")

### bars

## bars for simulations
# Counts per EONR for Simulated data
results_region_filtered['Yield']=results_region_filtered['Yield']
idx_max_yield=results_region_filtered.groupby('id_GTD')['Yield'].idxmax()
max_yield_df = results_region_filtered.loc[idx_max_yield, ['id_GTD', 'Nitrogen']].set_index('id_GTD')

# map nitrogen at max yield 
results_region_filtered['nrate_max_yield'] = results_region_filtered['id_GTD'].map(max_yield_df['Nitrogen'])

# counting for simulations
sim_counts = (
    results_region_filtered
    .groupby(['region', 'nrate_max_yield'])
    .size()   
    .reset_index(name='count')  
)

sim_counts['Source']='Simulated'

## bars for GTD
GTD_filtered['Nitrogen'] = GTD_filtered['NKg_Ha'] 
GTD_filtered['id_real']=np.arange(len(GTD_filtered))//4
GTD_filtered['Yield']=GTD_filtered['Yield'].astype(int)
idx_max_yield=GTD_filtered.groupby('id_real')['Yield'].idxmax()
max_yield_df = GTD_filtered.loc[idx_max_yield, ['id_real', 'Nitrogen']].set_index('id_real')


GTD_filtered['nrate_max_yield'] = GTD_filtered['id_real'].map(max_yield_df['Nitrogen'])

gtd_counts = (
    GTD_filtered
    .groupby(['region', 'nrate_max_yield'])
    .size()   # count rows in each group
    .reset_index(name='count')  # convert to DataFrame with column 'count'
)
gtd_counts['Source']='Ground Truth'

# merging counts
total_counts=pd.concat([sim_counts,gtd_counts])
total_counts['total']=total_counts.groupby(['region','Source'])['count'].transform('sum')
total_counts['percentage']=total_counts['count']/total_counts['total']*100

bars_plot = (
    ggplot(total_counts, aes(x='nrate_max_yield',y='percentage',fill='region'))
    + geom_col(position='dodge', width=100,color='black')
    + theme_bw()
    + facet_grid('Source~region')
    + labs(x='Economical Optimum N Rate (Kg/ha)',y="% of sites",fill='Region')
)

bars_plot.save("/workspace/calibration/_6EvaluationNotebooks/PaperViz/barsPaper.jpeg")

### Nitrogen Leaching
