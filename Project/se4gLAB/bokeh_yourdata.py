#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:46:57 2020

@author: chiarapileggi
"""


#Importing the required packages
import pandas as pd
import geopandas as gpd
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
#from bokeh.tile_providers import get_provider, Vendors #bokeh version 1.1
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from psycopg2 import connect

def getPointCoords(rows, geom, coord_type):
   """Calculates coordinates ('x' or 'y') of a Point geometry"""
   if coord_type == 'x':
        return rows[geom].x
   elif coord_type == 'y':
        return rows[geom].y
    
def funct_DB_visua():
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
    cur = conn.cursor()

    cur.execute("SELECT latitude,longitude,dieback,diameter,height,species,author_id FROM data")
    data = cur.fetchall()
    data_df = pd.DataFrame(data,columns=['latitude', 'longitude', 'dieback','height','diameter','species','author_id'])

    data_df['lat'] = pd.to_numeric(data_df['latitude'], errors='coerce') 
    data_df['lon'] = pd.to_numeric(data_df['longitude'], errors='coerce')
    data_df['diam']=pd.to_numeric(data_df['diameter'],errors='coerce')
    data_df['db']= pd.to_numeric(data_df['dieback'],errors='coerce')
    data_df['height']=pd.to_numeric(data_df['height'],errors='coerce')
    data_df['species']=pd.to_numeric(data_df['species'],errors='ignore')
    data_df['author_id']=pd.to_numeric(data_df['author_id'], errors = 'ignore')

    Data= gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['lon'], data_df['lat']))
    Data.crs= '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    Data.to_file(r'C:\Users\maria\Desktop\Desktop.shp')

    Data = gpd.read_file(r"C:\Users\maria\Desktop\Desktop.shp").to_crs(epsg=3857)



    
    Data['x'] = Data.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    Data['y'] = Data.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)

#Save the coordinates as attributes in a new dataframe
    data_df = Data.drop('geometry', axis=1).copy()

#Use the dataframe as Bokeh ColumnDataSource
    psource = ColumnDataSource(data_df)

#Specify feature of the Hoover tool
    TOOLTIPS = [
    ("author_id","@author_id"),
    ("species","@species"),
    ("dieback","@db"),
    ("height","@height"),
    ("diameter","@diam")
    ]
    


#Create the Map plot

# range bounds supplied in web mercator coordinates epsg=3857

    p2 = figure(x_range=(-9643000,-9639000), y_range=(5018080,5021599),
               x_axis_type="mercator", y_axis_type="mercator", tooltips=TOOLTIPS)

#Add basemap tile
#p1.add_tile(get_provider(Vendors.CARTODBPOSITRON)) #bokeh version 1.1
#questo comando potrebbe variare a seconda della versione! la mia è 3.7
    tile_provider = get_provider(CARTODBPOSITRON)
    p2.add_tile(tile_provider)

#Add Glyphs
    p2.circle('x', 'y', source=psource, color='red', radius=10) #size=10

#Add Labels and add to the plot layout
    labels = LabelSet(x='x', y='y', text='index',
              x_offset=5, y_offset=5, source=psource, render_mode='css')
		  
    p2.add_layout(labels)

#Output the plot
    output_file(r"C:\Users\maria\Desktop\se4gLAB\templates\yourData_map.html")
    show(p2)
    return

