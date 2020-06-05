import requests
import pandas as pd
import json
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, Select
from bokeh.io import curdoc
from bokeh.layouts import row
from bokeh.palettes import Spectral11

response = requests.get('https://five.epicollect.net/api/export/entries/winamac-trees?per_page=1341')
raw_data = response.text
data = json.loads(raw_data)
data_df = pd.json_normalize(data['data']['entries'])

tree = pd.DataFrame()


tree['diam']=pd.to_numeric(data_df['19_Diameter_at_Breas'],errors='coerce')
tree['dieback']= pd.to_numeric(data_df['9_Dieback__percent'],errors='coerce')
tree['height']=pd.to_numeric(data_df['20_Height'],errors='coerce')
tree['address']=pd.to_numeric(data_df['title'],errors='ignore')

tree = tree.loc[(tree['diam'] != 0) & (tree['height'] != 0)]

rename = []

for i in tree['address']:
    if 'Market' in i:
        rename.append('Market Street')
    elif 'Riverside' in i:
        rename.append('Riverside Street')
    elif 'Monticello' in i:
        rename.append('Monticello Street')
    elif 'Main' in i:
        rename.append('Main Street')
    elif 'Northwest' in i:
        rename.append('Nortwest Street')
    elif 'West Street' in i :
        rename.append('West Street')
    elif 'Frenklin' in i:
        rename.append('Frenklin Street')
    elif 'Agnew' in i:
        rename.append('Agnew Street')
    elif 'Hathaway' in i:
        rename.append('Hataway Street')
    elif 'Logan' in i:
        rename.append('Logan Street')
    elif 'Burson' in i:
        rename.append('Burson Street')        
    else:
        rename.append('Other Streets')

tree['address'] = rename

widget_opt = list(tree) 
del widget_opt[3] 

tree_grouped = tree.groupby('address', axis=0).median()

options=[] #Empty List -> quello che voglio far vedere nel mio select widget

for i in widget_opt:
    string = '%s' %i
    options.append(string) 


street = list(tree_grouped.index) 
x = street
data = ColumnDataSource({'x' : x, 'y': list(tree_grouped['diam']), 'color' : Spectral11})

p2 = figure(x_range = x, y_range = (0,60))
p = figure(x_range=x, title = 'Suca')
p2.vbar(x='x', top='y', color = 'color',source = data, width=0.7, legend_field = "x")
p2.legend.orientation = "vertical"
p2.legend.location = "top_left"
p2.xaxis.major_label_orientation = 1.2


select_widget = Select(options = options, value = widget_opt[0], title = 'Select a Variable')

def callback(attr, old, new):
    column2plot = select_widget.value
    data.data = {'x' : x, 'y': list(tree_grouped[column2plot]), 'color' : Spectral11}
    p2.vbar(x='x', top='y' , source = data, color = 'color' , width=0.9, legend_field ="x")
    p2.legend.orientation = "vertical"
    p2.legend.location = "top_left"
    p2.xaxis.major_label_orientation = 1.2

select_widget.on_change('value', callback)

layout = row(select_widget, p2)

output_file('templates/prova_isto.html')
show(layout)
curdoc().add_root(layout)

