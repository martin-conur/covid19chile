#data manipulation
import json
import pandas as pd
import datetime as dt
import numpy as np

#dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

#links and references
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
token = 'pk.eyJ1Ijoicml0bWFuZG90cHkiLCJhIjoiY2s3ZHJidGt0MDFjNzNmbGh5aDh4dTZ0OSJ9.-SROtN91ZvqtFpO1nGPFeg'

#df links

#FUNCTIONS
#centroids of a polygon
def centroid(geometry):
    x = np.array(geometry[0])[:,0]
    y = np.array(geometry[0])[:,1]
    cen_x = sum(x)/len(x)
    cen_y = sum(y)/len(y)
    if type(cen_x) ==np.dtype(np.float64):
        return cen_x, cen_y
    else:
        return cen_x
#loading comunas
with open('geojson/comunas.geojson') as json_file:
    geojson_comunas = json.load(json_file)
#loading comunas
with open('geojson/regiones.geojson') as json_file:
    geojson_regiones = json.load(json_file)

#region names
region_names = {15: 'Arica y Parinacota',
                 1: 'Tarapacá',
                 2: 'Antofagasta',
                 3: 'Atacama',
                 4: 'Coquimbo',
                 5: 'Valparaíso',
                 13: 'Metropolitana',
                 6: 'O’Higgins',
                 7: 'Maule',
                 16: 'Ñuble',
                 8: 'Biobío',
                 9: 'Araucanía',
                 14: 'Los Ríos',
                 10: 'Los Lagos',
                 11: 'Aysén',
                 12: 'Magallanes',
                 0:'Todas las regiones'}

region_center = {11: (-75.50096893, -48.60930634),
                 2: (-69.30046955072464, -23.513314398840592),
                 9: (-72.21119059695653, -38.69860242717392),
                 15: (-70.28399658, -19.11595917),
                 3: (-69.95640176646154, -27.569922168923075),
                 8: (-72.56162326936172, -37.54021039914894),
                 4: (-70.81710363918369, -30.67727190142857),
                 6: (-71.12630634967742, -34.43829591870968),
                 10: (-73.0, -41.2),
                 14: (-72.43220677088233, -40.00901682235294),
                 12: (-69.26139069, -55.20180511),
                 7: (-71.27427253750001, -35.588552379999996),
                 16: (-71.90628936840001, -36.613470154400005),
                 13: (-70.67288351031247, -33.61857366562501),
                 1: (-69.38311566842106, -20.137420001842106),
                 5: (-71.12692737575001, -32.930289125250006)}
#APP
app = dash.Dash(__name__, external_stylesheets=external_css, external_scripts=external_js)

server = app.server
#supress callbacks exceptions
app.config.suppress_callback_exceptions = True
#the layout
app.layout = html.Div(children=[
    html.Div(
        className="app-header",
        children=[
            html.Div([html.Span('Planton', style={'color': '#5c75f2', 'font-style': 'italic', 'font-weight': 'bold'}),
                      html.Span(' Andino', style={'color': '#4FD7EC', 'font-style': 'italic', 'font-weight': 'bold'}),
                      html.Span(' spa', style={'color': 'gray', 'font-style': 'italic'})])
                      ], style={'margin-bottom':30},
            ),
            html.H3([html.Span('CENTRO DE DATOS:', style={'font-weight': 'bold'}),
                     html.Span(' covid19 en Chile', style={'font-style': 'italic'})], style={'margin-bottom':30}),

            html.H6('filtrar por:'),
            html.Div([
                dcc.Dropdown(id='dataset_dropdown',
                            options = [{'label':'Casos Confirmados Acumulados', 'value':'CC'},
                                        {'label':'Casos Activos', 'value':'CA'},
                                        {'label':'Zonas en Cuarentena', 'value':'ZC'},
                                        {'label':'Estadística', 'value':'EST'},
                                        ],
                            value ='CC',
                            style={'margin-bottom':10},
                            className = 'col s12 m12 l6'),
                dcc.Dropdown(
                            id='comuna_dropdown',
                            options = [
                                {'label':region_names[i], 'value':i} for i in range(17)],
                            value = 0,
                            className = 'col s12 m12 l6',
                            style={'margin-bottom':10, 'display':'none'})], className ='row'),
            html.Div(children= html.Div(id ='graphs'),className='row')
                 ],style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000, 'margin-buttom':20, 'heigth':'120vh', 'max-height':'140vh'})


#zonas de cuarentena callback
@app.callback(
    Output('comuna_dropdown','style'),
    [Input('dataset_dropdown','value')]
)
def cuarentena_callback(value):
    if value =='ZC':
        return {'display':'none'}
    else:
        return {'display':'block'}

#graphs callbacks
@app.callback(
    Output('graphs', 'children'),
    [Input('dataset_dropdown', 'value'),
     Input('comuna_dropdown', 'value')]
)

def graph_updater(dataset_value, comuna_value):
    graphs = []

    if dataset_value == 'CC':

        df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosAcumuladosPorComuna.csv")
        if comuna_value != 0:
            df = df.loc[df['Codigo region'] == comuna_value]

        fig = go.Figure(go.Choroplethmapbox(geojson=geojson_comunas, locations=df.Comuna, z=df[df.columns[-2]],
                                    colorscale="Reds", zmin=0, zmax=100, showscale = False,
                                    marker_opacity=0.9, marker_line_width=0.01, featureidkey='properties.comuna'))
        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token, autosize = True)
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, title_text = f"Casos confirmados acumulados al {df.columns[-2]}")

        #centering and zooming depending on the region
        if comuna_value == 0:
            fig.update_layout(mapbox_zoom=3, mapbox_center = {"lat": -37.0902, "lon": -72.7129})
        else:
            fig.update_layout(mapbox_zoom=7.5, mapbox_center = {"lat": region_center[comuna_value][1], "lon": region_center[comuna_value][0]})


        #bar graph
        df = df.dropna()
        df = df.sort_values(by=df.columns[-2], ascending = True)
        bar_fig = go.Figure(data=(go.Bar(y = df['Comuna'], x=df[df.columns[-2]],
                                text = df[df.columns[-2]], orientation = 'h', textposition = 'outside')),
                       layout = (go.Layout(xaxis={'showgrid':False, 'ticks':'', 'showticklabels':False}, yaxis={'showgrid':False})))
        if comuna_value != 0:
            bar_fig.update_layout(yaxis={'tickmode':'linear'})

        bar_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, autosize = True)
        bar_fig.update_layout(title_text = f'Casos confirmados acumulados al {df.columns[-2]}| Top Comunas')

        graphs.append(html.Div(dcc.Graph(
                                        id = 'mapa',
                                        figure = fig,
                                        style = {'height':'100vh'}
                                        ), className = 'col s12 m12 l6'))
        graphs.append(html.Div(dcc.Graph(
                                        id = 'scatter',
                                        figure = bar_fig,
                                        style = {'height':'100vh'}), className='col s12 m12 l6'))

    if dataset_value== 'ZC':
        import requests
        cuarentena = 'https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/Cuarentenas/Cuarentenas-Geo.geojson'
        geo_cuarentena = requests.get(cuarentena).json()
        info_cuarentena = []
        for feature in geo_cuarentena['features']:
            if feature['properties']['Estado'] ==1:
                info_cuarentena.append({'Nombre':feature['properties']['Nombre'],
                                  'Estado':feature['properties']['Estado'],
                                  'Fecha_Inicio':dt.datetime.utcfromtimestamp(feature['properties']['FInicio']//1000).strftime("%d/%m/%Y"),
                                  'Fecha_Termino':dt.datetime.utcfromtimestamp(feature['properties']['FTermino']//1000).strftime("%d/%m/%Y"),
                                  'Detalle':feature['properties']['Detalle'],
                                  'latitude':centroid(feature['geometry']['coordinates'])[-1],
                                  'longitude':centroid(feature['geometry']['coordinates'])[0]
                                 })

        cuarentena_df = pd.DataFrame(info_cuarentena)
        #just the 1 state (active quarentine)
        cuarentena_df=cuarentena_df.loc[cuarentena_df['Estado']==1]
        cuarentena_df = cuarentena_df.fillna('Sin Información')

        #the quarentine table
        table = go.Figure([go.Table(
            header=dict(values = ['Comuna', 'Fecha Inicio', 'Fecha Termino', 'Detalle'],
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[cuarentena_df['Nombre'], cuarentena_df['Fecha_Inicio'],
                                cuarentena_df['Fecha_Termino'], cuarentena_df['Detalle']],
                      align = 'left'))
        ])
        table.update_layout(margin={"r":10,"t":30,"l":0,"b":20}, height = 700, title = 'Zonas en Cuarentena')
        #table.update_layout(plot_bgcolor =plt_background, paper_bgcolor=plt_background)

        #quarentine map

        px.set_mapbox_access_token(token)
        map = px.scatter_mapbox(cuarentena_df, lat="latitude", lon="longitude",
                                size= 'Estado',size_max=40, zoom=2, text = 'Nombre')
        map.update_layout(mapbox_style = 'light',mapbox_zoom=3.1, mapbox_center = {"lat": -36.8, "lon": -73.5}, title_text='Mapa Cuarentena')
        map.update_layout(margin={"r":10,"t":30,"l":0,"b":0}, height = 700)
        #map.update_layout(plot_bgcolor =plt_background, paper_bgcolor=plt_background)

        graphs.append(html.Div(dcc.Graph(
                                        id = 'table',
                                        figure = table
                                        ), className = 'col s12 m12 l7'))
        graphs.append(html.Div(dcc.Graph(
                                        id = 'mapa',
                                        figure = map
                                        ), className = 'col s12 m12 l5'))

    if dataset_value == 'CA':
        df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosActualesPorComuna.csv")
        if comuna_value != 0:
            df = df.loc[df['Codigo region'] == comuna_value]
        fig = go.Figure(go.Choroplethmapbox(geojson=geojson_comunas, locations=df.Comuna, z=df[df.columns[-1]],
                                    colorscale="Reds", zmin=0, zmax=100, showscale = False,
                                    marker_opacity=0.9, marker_line_width=0.01, featureidkey='properties.comuna'))
        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height = 700, title_text= f'Mapa Casos activos al {df.columns[-1]}')
        #centering and zooming depending on the region
        if comuna_value == 0:
            fig.update_layout(mapbox_zoom=3, mapbox_center = {"lat": -37.0902, "lon": -72.7129})
        else:
            fig.update_layout(mapbox_zoom=7.5, mapbox_center = {"lat": region_center[comuna_value][1], "lon": region_center[comuna_value][0]})


        #bar graph
        df = df.dropna()
        df = df.sort_values(by=df.columns[-1], ascending = True)
        bar_fig = go.Figure(data=(go.Bar(y = df['Comuna'], x=df[df.columns[-1]],
                            text = df[df.columns[-1]], orientation = 'h', textposition = 'outside')),
                            layout = (go.Layout(xaxis={'showgrid':False, 'ticks':'', 'showticklabels':False}, yaxis={'showgrid':False})))

        bar_fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=700)
        bar_fig.update_layout(title_text =f'Casos activos al {df.columns[-1]}| Top Comunas')
        if comuna_value != 0:
            bar_fig.update_layout(yaxis={'tickmode':'linear'})


        #appending
        graphs.append(html.Div(dcc.Graph(
                                        id = 'mapa',
                                        figure = fig
                                        ), className = 'col s12 m12 l6'))
        graphs.append(html.Div(dcc.Graph(
                                        id = 'scatter',
                                        figure = bar_fig,
                                        ), className='col s12 m12 l6'))



    return graphs


if __name__ == '__main__':
    app.run_server(debug=True)
