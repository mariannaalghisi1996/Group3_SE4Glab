import requests
import pandas as pd
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt 
import json
from pandas.io.json import json_normalize
from bokeh.plotting import figure, show, output_file

def f_static():
    response = requests.get('https://five.epicollect.net/api/export/entries/winamac-trees?per_page=1341')

    raw_data = response.text

    data = json.loads(raw_data)

    data_df = json_normalize(data['data']['entries'])

    #1______come caratteristiche per ora ho messo: diametro, altezza, specie, indirizzo, condizione e dieback

    data_df['lat'] = pd.to_numeric(data_df['4_GPS_Location__Nort.latitude'], errors='coerce') 
    data_df['lon'] = pd.to_numeric(data_df['4_GPS_Location__Nort.longitude'], errors='coerce')
    data_df['diam']=pd.to_numeric(data_df['19_Diameter_at_Breas'],errors='coerce')
    data_df['db']= pd.to_numeric(data_df['9_Dieback__percent'],errors='coerce')
    data_df['height']=pd.to_numeric(data_df['20_Height'],errors='coerce')
    data_df['species']=pd.to_numeric(data_df['7_Species'],errors='ignore')
    data_df['address']=pd.to_numeric(data_df['title'],errors='ignore')
    data_df['condition']=pd.to_numeric(data_df['8_Condition'],errors='ignore')
 
    #Study distribution: subplots 
    f, axes = plt.subplots(3,1, sharex=True)
    sns_plot=sns.distplot( data_df["diam"] , color="skyblue", ax=axes[0]) 
    sns.distplot( data_df["db"] , color="olive", ax=axes[1])
    sns.distplot( data_df["height"] , color="gold", ax=axes[2]) 

    fig = sns_plot.get_figure()
    fig.savefig(r"C:\Users\maria\Desktop\se4gLAB\images\subplot_distribution.png")

    # Scatter the points
    #2 ______For height  
    lat, lon = data_df['lat'], data_df['lon'] 
    height, diam= data_df['height'], data_df['diam']
    sns_plot=plt.scatter(lon, lat, label=None, c=height, cmap='viridis', linewidth=0, alpha=0.5) 
    plt.axis(aspect='equal')
    plt.xlabel('longitude') 
    plt.ylabel('latitude') 
    plt.colorbar(label='height') 
    plt.ticklabel_format(axis="both", style='plain', scilimits=(0,0), useMathText=True)
    plt.clim(0, 100)
    plt.grid()
    plt.show()

    fig = sns_plot.get_figure()
    fig.savefig(r"C:\Users\maria\Desktop\se4gLAB\images\scatter_height.png")

    #3_____For diameter  
    lat, lon = data_df['lat'], data_df['lon'] 
    height, diam= data_df['height'], data_df['diam']
    sns_plot=plt.scatter(lon, lat, label=None, c=diam, cmap='viridis', linewidth=0, alpha=0.5) 
    plt.axis(aspect='equal')
    plt.xlabel('longitude') 
    plt.ylabel('latitude') 
    plt.colorbar(label='diam') 
    plt.ticklabel_format(axis="both", style='plain', scilimits=(0,0), useMathText=True)
    plt.clim(0, 90)
    plt.grid()
    plt.show()

    fig = sns_plot.get_figure()
    fig.savefig(r"C:\Users\maria\Desktop\se4gLAB\templates\images\scatter_diam.png")
    
    return
