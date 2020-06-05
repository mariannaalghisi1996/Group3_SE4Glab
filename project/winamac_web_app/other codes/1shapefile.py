import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import json
import geopandas as gpd
import contextily as ctx


response = requests.get('https://five.epicollect.net/api/export/entries/winamac-trees?per_page=1341')

raw_data = response.text

data = json.loads(raw_data)

data_df = pd.json_normalize(data['data']['entries'])

data_df['lat'] = pd.to_numeric(data_df['4_GPS_Location__Nort.latitude'], errors='coerce') 
data_df['lon'] = pd.to_numeric(data_df['4_GPS_Location__Nort.longitude'], errors='coerce')
data_df['diam']=pd.to_numeric(data_df['19_Diameter_at_Breas'],errors='coerce')
data_df['db']= pd.to_numeric(data_df['9_Dieback__percent'],errors='coerce')
data_df['height']=pd.to_numeric(data_df['20_Height'],errors='coerce')
data_df['species']=pd.to_numeric(data_df['7_Species'],errors='ignore')
data_df['address']=pd.to_numeric(data_df['title'],errors='ignore')
data_df['condition']=pd.to_numeric(data_df['8_Condition'],errors='ignore')

data_geodf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['lon'], data_df['lat']))
data_geodf.plot()

n=len(data_df)

from shapely.geometry import Point

trees = gpd.GeoDataFrame()
trees['geometry']= None

for i in range(n):
    condition=data_df.loc[i,'condition']
    address=data_df.loc[i,'address']
    species=data_df.loc[i,'species']
    dieback=data_df.loc[i,'db']
    height=data_df.loc[i,'height']
    diameter=data_df.loc[i,'diam']
    latitude=data_df.loc[i,'lat']
    longitude= data_df.loc[i,'lon']
    P=Point(longitude,latitude)
    trees.loc[i,'geometry']=P
    trees.loc[i,'diameter']=diameter
    trees.loc[i,'height']=height
    trees.loc[i,'dieback']=dieback
    trees.loc[i,'species']=species
    trees.loc[i,'latitude']=latitude
    trees.loc[i,'longitude']=longitude
    trees.loc[i,'address']= address
    trees.loc[i,'condition']=condition

f_trees= trees[0:n:15]

f_trees.crs= '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

f_trees.to_file(r'/shapefile/shape1.shp')

gdf = gpd.read_file(r'/shapefile/shape1.shp').to_crs(epsg=3857)

#QUESTA PARTE E' SOLO PER VISUALIZZARE MAPPA
#aggiungo mappa
def add_basemap(ax, zoom, url='http://tile.stamen.com/terrain/tileZ/tileX/tileY.png'):
  xmin, xmax, ymin, ymax = ax.axis()
  basemap, extent = ctx.bounds2img(xmin, ymin, xmax, ymax, zoom=zoom, url=url) 
  ax.imshow(basemap, extent=extent, interpolation='bilinear')
# restore original x/y limits
  ax.axis((xmin, xmax, ymin, ymax))
  
ax = gdf.plot(figsize=(5,5), alpha=0.5, marker='o', color='red', edgecolor='k')

add_basemap(ax, zoom = 13)

