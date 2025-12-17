import pandas as pd
import numpy as np

# Importing GTD with curve parameters
GTD_raw=pd.read_csv("/workspace/GTD2.csv")
# Deleting rows without locations
GTD_raw.dropna(axis=0,inplace=True)

# Mapping region
region_mapping = {

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

# Setting rates of nitrogen
# nitro=[0,44.61,89.22,133.83,178.44,223.05,267.66]
nitro = [0,89.22,178.44,267.66]

# Variables of the new GTD
yield_ton=[]
NKg_Ha=[]
long=[]
lat=[]
county=[]
region=[]
year=[]

# Getting values from curve parameters
for idx,row in GTD_raw.iterrows():
    yield_per_place=[0]
    for rate in nitro:
        year.append(row['Year'])
        region.append(row['CRD'])
        county.append(row['County'])
        lat.append(row['Latitude'])
        long.append(row['Longitude'])
        NKg_Ha.append(int(rate/0.892))
        # Assuming that the formula is in bushes/acre (I think)
        yield_bush=float(row['a'])+float(row['b'])*rate-np.abs(float(row['c']))*(rate**2)
        ton=((yield_bush*60)*1.12085)/1000
        
        if yield_per_place[-1]==0:
            yield_per_place.append(ton)
            yield_ton.append(ton)
            
        elif ton < yield_per_place[-1]:
            yield_ton.append(yield_ton[-1])
            
        else:
            yield_ton.append(ton)
            yield_per_place.append(ton)  
    
        
       
# Creating new GTD2
GTDtransform=pd.DataFrame({
    'yield_ton':yield_ton,
    'NKg_Ha':NKg_Ha,
    'long':long,
    'lat':lat,
    'county':county,
    'region':region,
    'year':year
    })


county_map={
    "Tippecanoe": "Tippecanoe County",
    "Ripley": "Ripley County",
    "Hamilton": "Hamilton County",
    "Gibson": "Gibson County",
    "Vigo": "Vigo County",
    "Grant": "Grant County",
    "Randolph": "Randolph County",
    "Hendricks": "Hendricks County",
    "Lawrence": "Lawrence County",
    "Decatur": "Decatur County",
    "Whitley": "Whitley County",
    "Clay": "Clay County",
    "Henry": "Henry County",
    "Porter": "Porter County",
    "Jennings": "Jennings County",
    "Knox": "Knox County",
    "Benton": "Benton County",
    "Blackford": "Blackford County",
    "Pulaski": "Pulaski County",
    "Clinton": "Clinton County",
    "Lake": "Lake County",
    "Carroll": "Carroll County",
    "Adams": "Adams County",
    "Marshall": "Marshall County",
    "Elkhart": "Elkhart County",
    "Madison": "Madison County",
    "Johnson": "Johnson County",
    "Jasper": "Jasper County",
    "Cass": "Cass County",
    "Vanderburgh": "Vanderburgh County",
    "Shelby": "Shelby County",
    "La Porte": "Laporte County",
    "Miami": "Miami County"
}


valid_counties = list(county_map.keys())

GTDtransform = GTDtransform[GTDtransform["county"].isin(valid_counties)].copy()

GTDtransform["county"] = GTDtransform["county"].replace(county_map)

GTDtransform["region"] = GTDtransform["county"].map(region_mapping)

mask=(GTDtransform['yield_ton']>0)

GTDtransform=GTDtransform.loc[mask]

GTDtransform["location_id"] =GTDtransform.groupby(["long", "lat"]).ngroup()

GTDtransform['id_GTD'] = GTDtransform.apply(lambda row: f"{row['location_id']}_{row['year']}_N{row['NKg_Ha']}", axis=1)

GTDtransform.to_csv("/workspace/calibration/_1GTDtransform/GTDtransform.csv",index=False)