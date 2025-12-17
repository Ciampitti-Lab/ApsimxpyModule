import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPolygon

# Import GTD cleaned
GTD_transform=pd.read_csv("/workspace/calibration/_1GTDtransform/GTDtransform.csv")
# Getting the geometry using long and lat
GTD_transform['geometry'] = GTD_transform.apply(lambda row: Point(row['long'], row['lat']),axis=1)

GTD_points=gpd.GeoDataFrame(GTD_transform,
                           geometry='geometry',
                           crs='EPSG:4326')
# Getting all the poligons withinthe AOI
aoi_fields=gpd.read_file("/workspace/workflow/_2GridSampling/aoi_fields.geojson")
aoi_fields.to_crs('EPSG:4326',inplace=True)

# Select just polygons with points inside
GTD_fields_idx=gpd.sjoin(
    left_df=GTD_points,
    right_df=aoi_fields,
    how='inner',
    predicate='within'
)
GTD_fields = (
    GTD_fields_idx
    .merge(
        aoi_fields,
        left_on='index_right',
        right_index=True,
        how='left'
    )
)

GTD_fields=GTD_fields[['id_GTD','location_id','year','NKg_Ha','region','geometry_y']]
GTD_fields.columns=['id_GTD','location_id','year','NKg_Ha','region','geometry']
GTD_fields.drop_duplicates(inplace=True)
# Exporting selected polygons
GTD_fields.to_file("/workspace/calibration/_2FieldSelection/GTDfields.geojson",driver="GeoJSON")