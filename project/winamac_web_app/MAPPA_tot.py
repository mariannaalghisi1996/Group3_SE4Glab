#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 21:46:57 2020

@author: chiarapileggi
"""

#Importing the required packages
import bokeh
import geopandas as gpd
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
import pandas as pd
from psycopg2 import connect

#funzione  coordinate
def getPointCoords(rows, geom, coord_type):
   """Calculates coordinates ('x' or 'y') of a Point geometry"""
   if coord_type == 'x':
        return rows[geom].x
   elif coord_type == 'y':
        return rows[geom].y

#salvo dati su geodatabase Data
        
def funct_DB_visua():   
    myFile = open('dbConfig.txt')
    connStr = myFile.readline()
    conn = connect(connStr)
    cur = conn.cursor()

    cur.execute("SELECT latitude,longitude,dieback,diameter,height,species,author_id FROM data")
    data = cur.fetchall()
    data_df = pd.DataFrame(data,columns=['latitude', 'longitude', 'dieback','height','diameter','species','author_id'])

    data_df['latitude'] = pd.to_numeric(data_df['latitude'], errors='coerce') 
    data_df['longitude'] = pd.to_numeric(data_df['longitude'], errors='coerce')
    data_df['diameter']=pd.to_numeric(data_df['diameter'],errors='coerce')
    data_df['dieback']= pd.to_numeric(data_df['dieback'],errors='coerce')
    data_df['height']=pd.to_numeric(data_df['height'],errors='coerce')
    data_df['species']=pd.to_numeric(data_df['species'],errors='ignore')
    data_df['author_id']=pd.to_numeric(data_df['author_id'], errors = 'ignore')

    Data= gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['longitude'], data_df['latitude']))
    Data.crs= '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
  
    #salvo Data
    Data.to_file(r'shapefile/2shape.shp')


    #apro entrambi i shapefile
    stations = gpd.read_file("shapefile/shape1.shp").to_crs(epsg=3857)
    Data = gpd.read_file(r"shapefile/2shape.shp").to_crs(epsg=3857)
    


#apply function    
    stations['x'] = stations.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    stations['y'] = stations.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
    Data['x'] = Data.apply(getPointCoords, geom='geometry', coord_type='x', axis=1)
    Data['y'] = Data.apply(getPointCoords, geom='geometry', coord_type='y', axis=1)
    

    stations_df = stations.drop('geometry', axis=1).copy()
    Data_df = Data.drop('geometry', axis=1).copy()

#Use the dataframe as Bokeh ColumnDataSource
    psource = ColumnDataSource(stations_df)
    psource2 = ColumnDataSource(Data_df)

#Specify feature of the Hoover tool
    TOOLTIPS = [
   
        ("diameter", "@diameter"),
        ("height", "@height"),
        ("species","@species"),
        ("dieback","@dieback")
    
       ]

#Create the Map plot

# range bounds supplied in web mercator coordinates epsg=3857


    p1 = figure(x_range=(-9643000,-9639000), y_range=(5018080,5021599),
               x_axis_type="mercator", y_axis_type="mercator", tooltips=TOOLTIPS)

#Add basemap tile
#p1.add_tile(get_provider(Vendors.CARTODBPOSITRON)) #bokeh version 1.1
#questo comando potrebbe variare a seconda della versione! la mia è 3.7
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    p1.add_tile(tile_provider)

#Add Glyphs
    p1.circle('x', 'y', source=psource, color='red', radius=30) 
    p1.circle('x', 'y', source=psource2, color='blue', radius=30) 

#Add Labels and add to the plot layout
    labels = LabelSet(x='x', y='y', text='index',
              x_offset=5, y_offset=5, source=psource, render_mode='css')
		  
    p1.add_layout(labels)

#Output the plot
    output_file("templates/Trees_TOT.html")
    
    show(p1)
   
    error = None
    return error
