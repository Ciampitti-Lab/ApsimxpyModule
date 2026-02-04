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

gtd1=pd.read_csv("/usr/local/shared/indiana_nitrogen_initiative/camberato&nielsen_2006_2022/MasterDbase_NR_Dbase_forRstudio_0504.csv",encoding="latin",names=['id','prev_crop','pu','year','state','crd','county','location','fld','lat','long','sandy','muck','soil_texture','soil_assoc','manure','irrig','hybrid','plt_date','ntiming','nsource','model','a','b','c','aonr','opt_yield','rsq','eonr'])

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

# Getting yields from the curve
yield_bush = (
    gtd1['a'].astype(float)
    + gtd1['b'].astype(float) * gtd1['rate']
    - gtd1['c'].astype(float).abs() * gtd1['rate']**2
)

# from bushes to ton
gtd1['yield_ton'] = ((yield_bush * 60) * 1.12085) / 1000

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
# new_gtd1.to_csv('/workspace/workflow/_6EvaluationNotebooks/GTD.csv',index=False)
###############################################################################################################################
#                              NRCS_N_project_Indiana_dataset_2025.04.17_CSV.xlsx                                             #
###############################################################################################################################




