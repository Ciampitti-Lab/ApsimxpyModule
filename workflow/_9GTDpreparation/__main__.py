import pandas as pd
import numpy as np
import fit_curves
from fit_curves import *
#########################################################################################################################
#                                   MasterDbase_NR_Dbase_forRstudio_0504.csv                                            #
#########################################################################################################################


# Map information to get regions from counties

county_map={
    "Tippecanoe": "Tippecanoe County","Ripley": "Ripley County","Hamilton": "Hamilton County","Gibson": "Gibson County","Vigo": "Vigo County",
    "Grant": "Grant County","Randolph": "Randolph County","Hendricks": "Hendricks County","Lawrence": "Lawrence County","Decatur": "Decatur County",
    "Whitley": "Whitley County","Clay": "Clay County","Henry": "Henry County","Porter": "Porter County","Jennings": "Jennings County","Knox": "Knox County",
    "Benton": "Benton County","Blackford": "Blackford County","Pulaski": "Pulaski County","Clinton": "Clinton County","Lake": "Lake County","Carroll": "Carroll County",
    "Adams": "Adams County","Marshall": "Marshall County","Elkhart": "Elkhart County","Madison": "Madison County","Johnson": "Johnson County","Jasper": "Jasper County",
    "Cass": "Cass County","Vanderburgh": "Vanderburgh County","Shelby": "Shelby County","La Porte": "Laporte County","Miami": "Miami County"
}

region3_map = {

    "Jasper County": "NC", "Lake County": "NC", "Laporte County": "NC", "Newton County": "NC", "Porter County": "NC", "Pulaski County": "NC", "Starke County": "NC", "White County": "NC",
    "Kosciusko County":"NC","Wabash County":"NC","St Joseph County":"NC","Cass County": "NC", "Fulton County": "NC", "Howard County": "C", "Miami County": "NC", "Tippecanoe County": "NC", "Tipton County": "C", "Carroll County": "NC", "Clinton County": "C","Marshall County":"NC","Elkhart County":"NC",
    "Adams County": "NE", "Allen County": "NE", "Dekalb County": "NE", "Huntington County": "NE", "Lagrange County": "NE", "Noble County": "NE", "Steuben County": "NE", "Wells County": "NE", "Whitley County": "NE",
    "Benton County": "NC", "Fountain County": "NC", "Montgomery County": "NC", "Parke County": "NC", "Putnam County": "NC", "Vermillion County": "NC", "Warren County": "NC","Vigo County": "NC","Clay County": "NC",
    "Boone County": "C", "Hamilton County": "C", "Hancock County": "C", "Hendricks County": "C", "Johnson County": "C", "Madison County": "C", "Marion County": "C", "Morgan County": "C", "Shelby County": "C",
    "Blackford County": "NE","Union County": "NE","Fayette County": "NE", "Delaware County": "NE", "Grant County": "C", "Henry County": "NE", "Jay County": "NE", "Randolph County":"NE","Rush County":"C","Wayne County":"NE",    
    "Daviess County": "NC", "Sullivan County": "NC","Gibson County": "NC", "Knox County": "NC", "Perry County": "NC", "Pike County": "NC", "Posey County": "NC", "Spencer County": "NC", "Vanderburgh County": "NC", "Warrick County": "NC",
    "Brown County": "NC", "Crawford County": "NC", "Dubois County": "NC", "Greene County": "NC", "Lawrence County": "NC", "Martin County": "NC", "Monroe County": "NC", "Orange County": "NC", "Owen County": "NC", "Washington County": "NC",
    "Bartholomew County": "C", "Clark County": "NC", "Decatur County": "C", "Dearborn County": "NC", "Floyd County": "NC", "Franklin County": "NC", "Harrison County": "NC", "Jackson County": "NC", "Jefferson County": "NC", "Jennings County": "NC", "Ohio County": "NC", "Ripley County": "NC", "Scott County": "NC", "Switzerland County": "NC"
}

gtd1=pd.read_csv("/workspace/workflow/_9GTDpreparation/MasterDbase_NR_Dbase_forRstudio_0504.csv",encoding="latin",names=['id','prev_crop','pu','year','state','crd','county','location','fld','lat','long','sandy','muck','soil_texture','soil_assoc','manure','irrig','hybrid','plt_date','ntiming','nsource','model','a','b','c','aonr','opt_yield','rsq','eonr'])

# Filtering rows
gtd1 = gtd1[gtd1['manure']=='no'] # No Manure
gtd1 = gtd1[gtd1['irrig']=='no'] # No Irrigation
gtd1 = gtd1[gtd1['prev_crop']=='Soy'] # Only Soybean as a Prep Crop


values_to_replace=['-','']
gtd1=gtd1.replace(values_to_replace,np.nan)
columns_to_check=['a','b','c']
gtd1.dropna(subset=columns_to_check,inplace=True)
gtd1.reset_index(drop=True, inplace=True)

# Selecting Columns
gtd1=gtd1[['id','year','crd','county','a','b','c','aonr']]


# Nitrogen dosis
nitro = np.random.uniform(0, 267.66, size=20)


# Setting all nitrogen dosis for each trial
gtd1 = (
    gtd1
    .assign(key=1)
    .merge(
        pd.DataFrame({'rate': nitro, 'key': 1}),
        on='key'
    )
    .drop(columns='key')
)

# from lb to kilograms
gtd1['nkg_ha'] = (gtd1['rate'] / 0.892).astype(int)

a = gtd1['a'].astype(float)
b = gtd1['b'].astype(float)
c = gtd1['c'].astype(float).abs()
r = gtd1['rate'].astype(float)
aonr = gtd1['aonr'].astype(float)

curve_val = a + (b * r) - (c * r**2)
plateau_val = a + (b * aonr) - (c * aonr**2)


gtd1['yield_bush'] = np.where(r <= aonr, curve_val, plateau_val)

gtd1['yield_ton'] = (gtd1['yield_bush'] * 60 * 1.12085) / 1000

# Enforcing non-decreasing yield per field
gtd1['yield_ton'] = (
    gtd1
    .sort_values('rate')
    .groupby('id')['yield_ton']
    .cummax()
)

# Static column
gtd1['dbase'] = 'GTD2'

# Setting Region
valid_counties = list(county_map.keys())

gtd1 = gtd1[gtd1["county"].isin(valid_counties)].copy()

gtd1["county"] = gtd1["county"].replace(county_map)

gtd1["region"] = gtd1["county"].map(region3_map)

gtd1['aonr']=gtd1['aonr'].astype('float')

new_gtd1=pd.DataFrame({
    'yield_ton_ha':gtd1['yield_ton'],
    'nitro_kg_ha':gtd1['nkg_ha'],
    'county':gtd1['county'],
    'region':gtd1['region'],
    'year':gtd1['year'],
    'id':gtd1['id'],
    'aonr':gtd1['aonr'],
    'dbase':gtd1['dbase']
    })

new_gtd1.to_csv('/workspace/workflow/_9GTDpreparation/new_gtd1.csv',index=False)
new_gtd1.to_csv('/workspace/workflow/_6EvaluationNotebooks/GTD.csv',index=False)
###############################################################################################################################
#                              NRCS_N_project_Indiana_dataset_2025.04.17_CSV.xlsx                                             #
###############################################################################################################################

gtd2 = pd.read_excel('/workspace/workflow/_9GTDpreparation/NRCS_N_project_Indiana_dataset_2025.04.17_CSV.xlsx',sheet_name='Data',header=3, names=['state','county','year','field','field_name','id','grid_id','grid_org','transects_n','transect_id','transect_r','trans_a','trans_b','strategy','pnm','fp','damage','area_ac','plot_id','trt_n','tratment','ref_block','rep_refb','pt_npass','sd_npass','hybrid','tile','pre_crop','tillage','fnr_lbac','r_exn_lbac','r_stn_lbac','p_pren_lbac','r_pren_lbac','p_sidn_lbac','sidn_lbac','r_sdn_lbac','p_totn_lbac','rtn_lbac','rtotn_kgha','ryl15_buac','ry15_mtha'])
# Filtering rows
gtd2=gtd2[gtd2['pre_crop']=='Soybean']
# Selecting Columns 
gtd2=gtd2[['year','id','rtotn_kgha','ry15_mtha']]

# Here I just rounded the decimals and then I grouped by nrate to avoid repeated nrates
gtd2['rtotn_kgha'] = gtd2['rtotn_kgha'].div(10).astype('int')*10

gtd2 = gtd2.sort_values('rtotn_kgha')
gtd2 = gtd2.groupby(['rtotn_kgha','id'],as_index=False)['ry15_mtha'].mean()

# Selecting the best curve that fit each field
def fiting_curves(group):
    quad_r2 = fit_quadratic_plateau(group, 'ry15_mtha', "rtotn_kgha")['r2']
    lin_r2 = fit_linear_plateau(group, 'ry15_mtha', "rtotn_kgha")['r2']
    
    quad_rmse = fit_quadratic_plateau(group, 'ry15_mtha', "rtotn_kgha")['rmse']
    lin_rmse = fit_linear_plateau(group, 'ry15_mtha', "rtotn_kgha")['rmse']
    
    quad_b0 = fit_quadratic_plateau(group, 'ry15_mtha', "rtotn_kgha")['b0']
    lin_b0 = fit_linear_plateau(group, 'ry15_mtha', "rtotn_kgha")['b0']
    
    quad_b1 = fit_quadratic_plateau(group, 'ry15_mtha', "rtotn_kgha")['b1']
    lin_b1 = fit_linear_plateau(group, 'ry15_mtha', "rtotn_kgha")['b1']
    
    quad_b2 = fit_quadratic_plateau(group, 'ry15_mtha', "rtotn_kgha")['b2']

    
    return pd.Series({'quad_r2': quad_r2, 'lin_r2': lin_r2,'quad_rmse':quad_rmse ,'lin_rmse':lin_rmse,'quad_b0':quad_b0,'quad_b1':quad_b1,'quad_b2':quad_b2,'lin_b0':lin_b0 ,'lin_b1':lin_b1})
    
fit_results = gtd2.groupby('id',as_index=False).apply(fiting_curves, include_groups=True)

fit_results['best_model']=np.where(fit_results['quad_r2']>fit_results['lin_r2'],'quad_model','lin_model')


a=np.where(fit_results['best_model']=='quad_model',fit_results['quad_b0'],fit_results['lin_b0'])
b=np.where(fit_results['best_model']=='quad_model',fit_results['quad_b1'],fit_results['lin_b1'])
c=np.where(fit_results['best_model']=='quad_model',fit_results['quad_b2'],np.nan)

gtd2_curves=pd.DataFrame({
    'id':fit_results['id'],
    'a':a,
    'b':b,
    'c':c
    }
)

# Nitrogen dosis
nitro = np.random.uniform(0, 267.66, size=100)


gtd2_curves = (
    gtd2_curves
    .assign(key=1)
    .merge(
        pd.DataFrame({'rate': nitro, 'key': 1}),
        on='key'
    )
    .drop(columns='key')
)

a = gtd2_curves['a'].astype(float)
b = gtd2_curves['b'].astype(float)
c = gtd2_curves['c'].abs()
r = gtd2_curves['rate'].astype(float)

lin_val = a + (b * r)
quad_val =  a + (b * r) - (c * r **2)

gtd2_curves['yield_bush'] = np.where(gtd2_curves['c'].isna(),lin_val,quad_val)

gtd2_curves['yield_ton'] = (gtd2_curves['yield_bush'] * 60 * 1.12085) / 1000


