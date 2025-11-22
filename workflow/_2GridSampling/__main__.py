import geopandas as gpd
import numpy as np
from shapely.geometry import box

# Importing fields in the aoi
aoi_fields=gpd.read_file("/workspace/workflow/_2GridSampling/aoi_fields.geojson")
years_cols=['CDL2017', 'CDL2018', 'CDL2019', 'CDL2020', 
             'CDL2021', 'CDL2022', 'CDL2023', 'CDL2024']
aoi_fields['count_corn']=(aoi_fields[years_cols]==1).sum(axis=1)
aoi_corn_fields=aoi_fields[aoi_fields['count_corn']>=4]
aoi_corn_fields=aoi_corn_fields.reset_index(drop=True)
# Selecting just fields with more than 4 year of corn production
aoi_fields=gpd.read_file("/workspace/workflow/_2GridSampling/aoi_fields.geojson")
years_cols=['CDL2017', 'CDL2018', 'CDL2019', 'CDL2020', 
             'CDL2021', 'CDL2022', 'CDL2023', 'CDL2024']
aoi_fields['count_corn']=(aoi_fields[years_cols]==1).sum(axis=1)
aoi_corn_fields=aoi_fields[aoi_fields['count_corn']>=4]
aoi_corn_fields=aoi_corn_fields.reset_index(drop=True)

# Grid sampling
aoi_corn_fields=aoi_corn_fields.to_crs(epsg=26916)
minx, miny, maxx, maxy = aoi_corn_fields.total_bounds
grid_size = 10000  # 100 km

grid_cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        grid_cells.append(box(x, y, x + grid_size, y + grid_size))
        y += grid_size
    x += grid_size
grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs=aoi_corn_fields.crs)
aoi_corn_fields_grid = gpd.sjoin(aoi_corn_fields, grid, how='inner', predicate='intersects')
# Sampling within each cell --> Selecting 4 random fields
def sample_per_cell(gdf):
    return gdf.sample(n=min(4, len(gdf)), random_state=42)

field_final_sample = aoi_corn_fields_grid.groupby('index_right', group_keys=False).apply(sample_per_cell)
field_final_sample =field_final_sample.rename(columns = {'index_right':'id_cell'})
field_final_sample=field_final_sample.reset_index(drop=True)
field_final_sample['id_within_cell'] = (field_final_sample.groupby('id_cell').cumcount() + 1)
# Droping variables we don't need anymore
field_final_sample.drop(['CDL2017','CDL2018','CDL2019','CDL2020','CDL2021','CDL2022','CDL2023','CDL2024','count_corn'],axis=1,inplace=True)
field_final_sample.to_file("/workspace/workflow/_2GridSampling/field_final_sample.geojson",driver="GeoJSON")
print('Grid sampling sucessful!!! step 2/4')