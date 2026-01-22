import pandas as pd
import numpy as np

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

###############################################################################################################################
#                                                   NRCS N Project Indiana                                                    #
###############################################################################################################################
# Ground truth data (NRCS)
gtd1=pd.read_csv("/GTD1.csv")

# Filtering dataset by previous crop (Only Soybean)
gtd1=gtd1[gtd1['PreCrop']=='Soybean']

# Deleting no necessary columns 
gtd1.drop(['State','FieldName','PlotID','GridID','Trt_n','Grid_org','Transects_n','TransectID','Transect_R',
           'Trans_A','Trans_B','Strategy','PNM','FP','Damage','Area_ac','RepRefB','Pt_NPass','Sd_NPass','Hybrid',
           'Tile','PreCrop','Tillage','FNR_lbac','rExN_lbac','rStN_lbac','pPreN_lbac','rPreN_lbac','pSidN_lbac','SidN_lbac',
           'rSdN_lbac','pTotN_lbac','rTN_lbac','rYl15_buac'],axis=1,inplace=True)
# Fixing Years
gtd1['Year']=gtd1['Year']+2000

# Setting nitrogen rates
gtd1["Nitrogen"] = gtd1["rTotN_kgha"].round(2)

# Fixing counties
gtd1["county"] = gtd1["County"].replace({
    "White": "White County",
    "Randolph": "Randolph County",
    "Dubois": "Dubois County",
    "Marshall": "Marshall County",
    "Clay": "Clay County"
})

# Grouping trials 
new_gtd1 = (gtd1.groupby(["county", "Year", "Field", "FieldID", "Treatment", "Ref_block", "Nitrogen"],as_index=False).agg(Yield=("rY15_mtha", "mean")))

# Filtering trials with less than 3 nitrogen rates
new_gtd1 = new_gtd1[new_gtd1.groupby(["FieldID", "Treatment", "Ref_block"])["Nitrogen"].transform("count") >= 3]

# ID for each trial (Combination of FieldID, Treatment and Ref_block)
new_gtd1["id_trial"] = (
    new_gtd1
    .groupby(["FieldID", "Treatment", "Ref_block"])
    .ngroup()
)

# Setting region
new_gtd1["region"] = new_gtd1["county"].map(region3_map)

# GTD label
gtd_label=[]
for idx,row in new_gtd1.iterrows():
    gtd_label.append('GTD1')
    
new_gtd1['dbase']=gtd_label

# Deleting no necessary columns 
new_gtd1.drop(['Ref_block','Treatment','Field','FieldID'],axis=1,inplace=True)

new_gtd1.to_csv('/new_gtd1.csv',index=False)

# Still working in find the trials.

#########################################################################################################################
#                                                   MASTER DATABASE                                                     #
#########################################################################################################################

# Previous Cleaning
## Delete Manure == 1
## Delete Irrigation == 1


# Ground truth data (Master Database)
gtd2=pd.read_csv("/GTD2.csv")

# Setting rates of nitrogen (These are the values we will get the yield from the curves)
nitro = np.random.uniform(0, 267.66, size=100)

# Variables of the new GTD2
yield_ton=[]
NKg_Ha=[]
long=[]
lat=[]
county=[]
region=[]
year=[]
id_trial=[]
dbase=[]

field_id_map = {}
current_id=1
for idx,row in gtd2.iterrows():
    
    # Unique Key
    key = (row['Latitude'], row['Longitude'], row['Year'])
    
    if key not in field_id_map:
        field_id_map[key] = current_id
        current_id += 1

    this_field_id = field_id_map[key]
    
    yield_per_place=[0]
    for rate in nitro:
        year.append(row['Year'])
        region.append(row['CRD'])
        county.append(row['County'])
        lat.append(row['Latitude'])
        long.append(row['Longitude'])
        NKg_Ha.append(int(rate/0.892))
        id_trial.append(this_field_id)
        dbase.append('GTD2')
         # Assuming that the formula is in bushes/acre 
        yield_bush=float(row['a'])+float(row['b'])*rate-np.abs(float(row['c']))*(rate**2)
        ton=((yield_bush*60)*1.12085)/1000
        
        # Yield cannot decrease with increasing nitrogen   
        if yield_per_place[-1]==0:
            yield_per_place.append(ton)
            yield_ton.append(ton)
            
        elif ton < yield_per_place[-1]:
            yield_ton.append(yield_ton[-1])
            
        else:
            yield_ton.append(ton)
            yield_per_place.append(ton)  




# Creating new GTD2
new_gtd2=pd.DataFrame({
    'Yield':yield_ton,
    'Nitrogen':NKg_Ha,
    'county':county,
    'region':region,
    'Year':year,
    'id_trial':id_trial,
    'dbase':dbase
    })


valid_counties = list(county_map.keys())

new_gtd2 = new_gtd2[new_gtd2["county"].isin(valid_counties)].copy()

new_gtd2["county"] = new_gtd2["county"].replace(county_map)

new_gtd2["region"] = new_gtd2["county"].map(region3_map)

new_gtd2.to_csv('/new_gtd2.csv',index=False)
