import apsimxpy
import shapely
from apsimxpy.field.soil.ssurgo import sdapoly, sdaprop
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely import wkt

def get_poly_soil(polygon, plot=False)-> pd.DataFrame:
    # Wraping the polygon in a MultiPolygon
    if isinstance(polygon.geometry, shapely.Polygon):
        poly_geom = shapely.MultiPolygon([polygon.geometry])
    else:
        poly_geom = polygon.geometry
    
    
    # Creating a proper geospatial data structure # UTM Zone 16N
    df_poly = gpd.GeoDataFrame({'name': ['MyPoint']},
                            geometry=[poly_geom],
                            crs="EPSG:32616")
    
    # Getting all soils in the polygon 
    soils = sdapoly.gdf(df_poly)
    
    # Plotting the Field and all the soils
    if plot==True:
        soils_plot=soils.copy()
        soils_plot['geom'] = soils_plot['geom'].apply(wkt.loads)
        
        gdf_soils = soils_plot.set_geometry("geom")
        gdf_poly = soils_plot.set_geometry("geometry").drop_duplicates(subset=["geometry"])
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        gdf_soils.plot(ax=ax, alpha=0.5, edgecolor='black',facecolor='red')
        gdf_poly.plot(ax=ax, facecolor='lightgreen', edgecolor='black', linewidth=2)
        
        soil_patch = mpatches.Patch(facecolor='red', alpha=0.5, edgecolor='black',label='All Soils')
        poly_patch = mpatches.Patch(facecolor='lightgreen', edgecolor='black', label='Field')
        
        ax.legend(handles=[soil_patch, poly_patch], loc="upper right")

        ax.set_title("Soil Units Intersecting the Polygon")
        plt.show()
    else:
        pass
        
    return soils

# Getting the ID of the soil with more area covered in the polygon

def get_main_soil(soils, plot=False)-> int:
    
    # Calculate the area of each soil into the polygon
    soils["mukey"] = soils["mukey"].astype(int)
    soils["area_m2"] = soils["geometry"].to_crs(epsg=5070).area
    soils = soils.sort_values("area_m2", ascending=False).reset_index(drop=True)
    soils_id = soils.drop(["geom", "geometry"], axis=1)
    # Selecting the Mukey of the one with more area
    main_soil_id = int(soils_id['mukey'][soils_id['area_m2'] == soils_id['area_m2'].max()].iloc[0])
    
    # Plotting the Field, all the soils and the main soil
    if plot==True:
        soils_plot=soils.copy()
        soils_plot['geom'] = soils_plot['geom'].apply(wkt.loads)
        
        gdf_soils = soils_plot.set_geometry("geom")
        gdf_poly = soils_plot.set_geometry("geometry").drop_duplicates(subset=["geometry"])
        gdf_main=soils_plot[soils_plot['mukey']==main_soil_id]
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        gdf_soils.plot(ax=ax, alpha=0.5, edgecolor='black',facecolor='red')
        gdf_poly.plot(ax=ax, facecolor='lightgreen', edgecolor='black', linewidth=2)
        gdf_main.plot(ax=ax, alpha=0.5, edgecolor='black',facecolor='yellow')
        
        soil_patch = mpatches.Patch(facecolor='red', alpha=0.5, edgecolor='black',label='All Soils')
        poly_patch = mpatches.Patch(facecolor='lightgreen', edgecolor='black', label='Field')
        main_patch = mpatches.Patch(facecolor='yellow', edgecolor='black',label='Main Soil')
        
        ax.legend(handles=[soil_patch, poly_patch,main_patch], loc="upper right")

        ax.set_title("Main Soil In the Polygon")
        plt.show()
    else:
        pass
    
    return main_soil_id

def get_soil_props(soils,mukey_soil)-> pd.DataFrame:
    # It gets only variables for APSIM Simulation
    apsim_props = [
                'sandtotal_r', 'silttotal_r', 'claytotal_r',   # Sand, Silt, Clay
                'om_r',                                        # Carbon
                'dbovendry_r',                                 # BD
                'wtenthbar_r', 'wthirdbar_r', 'wfifteenbar_r', 'wsatiated_r', # AirDry , DUL, LL15, SAT
                'ksat_r',                                      # SWCON
                'cec7_r'                                       # CEC
            ]
    
    soil_props_ssurgo=pd.DataFrame() # Empty dataframe to collect all the properties of the soil
    for j in apsim_props:
        # Get the property only for the main soil and save it in the soil_props_ssurgo dataframe
        soil_features_df = sdaprop.getprop(df=soils,column='mukey',method='minmax',prop=j,minmax='MAX',prnt=False,meta=False).copy()
        soil_features_df = soil_features_df[soil_features_df['mukey'].astype(int)==mukey_soil]
        soil_features_df.reset_index(drop=True, inplace=True)
        soil_props_ssurgo[j]=soil_features_df[j]
    # Get the thickness of the horizons of the main-soil
    hzdept_r=soil_features_df['hzdept_r']
    hzdepb_r=soil_features_df['hzdepb_r']
    soil_props_ssurgo['thickness']=hzdept_r.astype(str)+'-'+hzdepb_r.astype(str)
    soil_props_ssurgo['hzdept_r']=hzdept_r
    soil_props_ssurgo['hzdepb_r']=hzdepb_r
    soil_props_ssurgo['center']=(soil_props_ssurgo["hzdept_r"].astype(float) + soil_props_ssurgo["hzdepb_r"].astype(float)) / 2
    soil_props_ssurgo['dbovendry_r']=soil_props_ssurgo['dbovendry_r'].astype(float)
    soil_props_ssurgo['sandtotal_r']=soil_props_ssurgo['sandtotal_r'].astype(float)
    soil_props_ssurgo['silttotal_r']=soil_props_ssurgo['silttotal_r'].astype(float)
    soil_props_ssurgo['claytotal_r']=soil_props_ssurgo['claytotal_r'].astype(float)
    soil_props_ssurgo['om_r']=soil_props_ssurgo['om_r'].astype(float)
    soil_props_ssurgo['ksat_r']=soil_props_ssurgo['ksat_r'].astype(float)
    soil_props_ssurgo['wtenthbar_r']=soil_props_ssurgo['wtenthbar_r'].astype(float)
    soil_props_ssurgo['wthirdbar_r']=soil_props_ssurgo['wthirdbar_r'].astype(float)
    soil_props_ssurgo['wfifteenbar_r']=soil_props_ssurgo['wfifteenbar_r'].astype(float)
    soil_props_ssurgo['wsatiated_r']=soil_props_ssurgo['wsatiated_r'].astype(float)
    soil_props_ssurgo['cec7_r']=soil_props_ssurgo['cec7_r'].astype(float)
    soil_props_ssurgo['hzdept_r']=soil_props_ssurgo['hzdept_r'].astype(float)
    soil_props_ssurgo['hzdepb_r']=soil_props_ssurgo['hzdepb_r'].astype(float)
    return soil_props_ssurgo
