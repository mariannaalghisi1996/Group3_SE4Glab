import requests
import pandas as pd
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt 
import json
from pandas.io.json import json_normalize
from bokeh.plotting import figure, show, output_file


response = requests.get('https://five.epicollect.net/api/export/entries/winamac-trees?per_page=1341')
raw_data = response.text
data = json.loads(raw_data)
data_df = pd.json_normalize(data['data']['entries'])
    
tree_df = pd.DataFrame()

tree_df['lat'] = pd.to_numeric(data_df['4_GPS_Location__Nort.latitude'], errors='coerce') 
tree_df['lon'] = pd.to_numeric(data_df['4_GPS_Location__Nort.longitude'], errors='coerce')
tree_df['diam']=pd.to_numeric(data_df['19_Diameter_at_Breas'],errors='coerce')
tree_df['db']= pd.to_numeric(data_df['9_Dieback__percent'],errors='coerce')
tree_df['height']=pd.to_numeric(data_df['20_Height'],errors='coerce')
tree_df['species']=pd.to_numeric(data_df['7_Species'],errors='ignore')
tree_df['address']=pd.to_numeric(data_df['title'],errors='ignore')
tree_df['condition']=pd.to_numeric(data_df['8_Condition'],errors='ignore')
    
tree_df = tree_df.loc[(tree_df['diam'] != 0) & (tree_df['height'] != 0) & (tree_df['diam']<55)]
   
 
    #1________Study distribution: subplots 
f, axes = plt.subplots(3,1, sharex=True)
sns.distplot( tree_df["diam"] , color="skyblue", ax=axes[0]) 
sns.distplot( tree_df["db"] , color="olive", ax=axes[1])
sns.distplot( tree_df["height"] , color="gold", ax=axes[2]) 
plt.show()

f.savefig("static\subplot_distribution.png")

    # Scatter the points
    #2 ______For height  
lat, lon = tree_df['lat'], tree_df['lon'] 
height, diam= tree_df['height'], tree_df['diam']
plot2=plt.scatter(lon, lat, label=None, c=height, cmap='viridis', linewidth=0, alpha=0.5) 
plt.axis(aspect='equal')
plt.xlabel('longitude') 
plt.ylabel('latitude') 
plt.colorbar(label='height') 
plt.ticklabel_format(axis="both", style='plain', scilimits=(0,0), useMathText=True)
plt.clim(0, 100)
plt.grid()
plt.show()

fig2 = plot2.get_figure()
fig2.savefig("static\scatter_height.png")

    #3_____For diameter  
plot3=plt.scatter(lon, lat, label=None, c=diam, cmap='viridis', linewidth=0, alpha=0.5) 
plt.axis(aspect='equal')
plt.xlabel('longitude') 
plt.ylabel('latitude') 
plt.colorbar(label='diam') 
plt.ticklabel_format(axis="both", style='plain', scilimits=(0,0), useMathText=True)
plt.clim(0, 55)
plt.grid()
plt.show()

fig3 = plot3.get_figure()
fig3.savefig("static\scatter_diam.png")
    
