from math import pi
from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum
import requests
import pandas as pd
import json
from pandas.io.json import json_normalize


response = requests.get('https://five.epicollect.net/api/export/entries/winamac-trees?per_page=1341')

raw_data = response.text

data = json.loads(raw_data)

data_df = json_normalize(data['data']['entries'])

#come caratteristiche per ora ho messo: diametro, altezza, specie, indirizzo, condizione e dieback

data_df['lat'] = pd.to_numeric(data_df['4_GPS_Location__Nort.latitude'], errors='coerce') 
data_df['lon'] = pd.to_numeric(data_df['4_GPS_Location__Nort.longitude'], errors='coerce')
data_df['diam']=pd.to_numeric(data_df['19_Diameter_at_Breas'],errors='coerce')
data_df['db']= pd.to_numeric(data_df['9_Dieback__percent'],errors='coerce')
data_df['height']=pd.to_numeric(data_df['20_Height'],errors='coerce')
data_df['species']=pd.to_numeric(data_df['7_Species'],errors='ignore')
data_df['address']=pd.to_numeric(data_df['title'],errors='ignore')
data_df['condition']=pd.to_numeric(data_df['8_Condition'],errors='ignore')

#ho selezionato solo gli alberi con altezza superiore a 60
High_height=data_df.loc[data_df["height"]>60]
species=High_height["species"]
#contare quanti elementi per ogni specie
Conto=species.value_counts()

#sistemare le colonne del dataframe e rinominarle
dati=Conto.reset_index(name='value').rename(columns={'index':'species'})

#aggiungere una colonna con l'angolo ed una con il colore
dati['angle'] = dati['value']/dati['value'].sum() * 2*pi
dati['color'] = Category20c[len(Conto)]

#plot
p = figure(plot_height=500,width=900, title="Pie Chart", toolbar_location=None,
           tools="hover", tooltips="@species: @value", x_range=(-0.5, 1.0))
#sistemare il layout
p.wedge(x=0, y=1, radius=0.3,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='species', source=dati)
p.legend.location = "top_right"
p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

show(p)
output_file("layout.html")