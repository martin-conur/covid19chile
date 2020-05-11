#data manipulation
import json
import pandas as pd
import datetime as dt
import numpy as np

#dash
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

#links and references

token = 'pk.eyJ1Ijoicml0bWFuZG90cHkiLCJhIjoiY2s3ZHJidGt0MDFjNzNmbGh5aDh4dTZ0OSJ9.-SROtN91ZvqtFpO1nGPFeg'
api = 'https://api.covid19api.com'

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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server = app.server
#supress callbacks exceptions
app.config.suppress_callback_exceptions = True

app.title = "Covidatos"
#the layout
app.layout = dbc.Container([
    html.Div(
        className="app-header",
        children=[
            html.Div(html.A([html.Span('Plancton', style={'color': '#5c75f2', 'font-style': 'italic', 'font-weight': 'bold'}),
                      html.Span(' Andino', style={'color': '#4FD7EC', 'font-style': 'italic', 'font-weight': 'bold'}),
                      html.Span(' SpA', style={'color': 'gray', 'font-style': 'italic'})], href ='https://plancton.cl/'))
                      ], style={'margin-bottom':30},
            ),
            html.H3([html.Span('CENTRO DE DATOS:', style={'font-weight': 'bold'}),
                     html.Span(' covid19 en Chile', style={'font-style': 'italic'})], style={'margin-bottom':30}),

            html.H6('filtrar por:'),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(id='dataset_dropdown',
                                    options = [ {'label':'Casos Confirmados Acumulados', 'value':'CC'},
                                                {'label':'Casos Activos', 'value':'CA'},
                                                {'label':'Series de tiempo interactivas', 'value':'ST'},
                                                {'label':'Zonas en Cuarentena', 'value':'ZC'},
                                                {'label':'Fallecidos, Críticos, UCI y respiradores', 'value':'EP'},
                                                {'label':'Síntomas de confirmados y hospitalizados', 'value':'ES'},
                                                {'label':'covid19 en el Mundo', 'value':'MUND'}
                                                ],
                                    value ='CC',
                                    style={'margin-bottom':10}
                                    ),
                                    lg=6
                            ),
                    dbc.Col(

                        dcc.Dropdown(
                                    id='comuna_dropdown',
                                    options = [{'label':region_names[i], 'value':i} for i in range(17)],
                                    value = 0,
                                    style={'margin-bottom':10, 'display':'none'}
                                    ),
                                    lg=6

                    )
                ]
            ),

            dbc.Row(children=[],id ='graphs'),
            html.Hr(),
            html.Footer("La fuente de los datos corresponde al repositorio del Ministerio de Ciencias y los informes Epistemiológicos"),
            html.Hr(),
            html.Footer(["Creado por ", html.A('@ritmandotpy', href='https://twitter.com/RitmanDotpy')]),
            html.Footer(" ")
                 ], fluid=True)


#zonas de cuarentena callback
@app.callback(
    Output('comuna_dropdown','style'),
    [Input('dataset_dropdown','value')]
)
def hide_dd_callback(value):
    if value in ['ZC', 'EP','ES','MUND']:
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

    if dataset_value == 'ST':
        activos_df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosActualesPorComuna.csv")
        activos = activos_df.melt(id_vars=["Region","Codigo region", "Comuna","Codigo comuna", "Poblacion"],
                          var_name="Fecha",
                          value_name="Activos")
        confirmados_df =  pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosAcumuladosPorComuna.csv")
        confirmados = confirmados_df.melt(id_vars=["Region","Codigo region", "Comuna","Codigo comuna", "Poblacion", "Tasa"],
                                          var_name="Fecha",
                                          value_name="Confirmados")

        #merging
        merged = confirmados.merge(activos, how ='inner')
        merged = merged.dropna()
        #filtering by comuna
        if comuna_value != 0:
            filtered_merge = merged.loc[merged['Codigo region'] == comuna_value]

        else:
            filtered_merge = merged
        #getting the filtered maxs
        max_confirmados = filtered_merge.Confirmados.max()*1.1 #+10%
        max_activos = filtered_merge.Activos.max()*1.1 #+10%
        max_tasa = filtered_merge.Tasa.max()*1.1
        #plotting
        double_scatter = px.scatter(filtered_merge, x="Confirmados", y="Activos", animation_frame="Fecha", animation_group="Comuna",
                                   size="Poblacion", color="Region", hover_name="Comuna", text='Comuna',
                                   log_x=False, range_y=[0,max_activos], range_x=[0,max_confirmados])
        double_scatter.update_layout(margin={"r":0,"t":50,"l":0,"b":0},
                                    title_text = "Casos Confirmados vs Activos actualmente: Serie de tiempo")
        double_scatter.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

        tasa = px.scatter(filtered_merge, x=filtered_merge.Confirmados*100000/filtered_merge.Poblacion, y="Activos", animation_frame="Fecha", animation_group="Comuna",
                                   size="Poblacion", color="Region", hover_name="Comuna", text='Comuna',
                                   log_x=False, range_y=[0,max_activos], range_x=[0,max_tasa])
        tasa.update_layout(margin={"r":0,"t":80,"l":0,"b":0},
                            title_text = "Tasa de Incidencia (cada 100k Hab.) vs casos activos",
                            xaxis_title = 'Casos Confirmados por 100 mil habitantes')
        tasa.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

        simple_scatter = px.scatter(merged, x="Region", y="Confirmados", color="Region",
                  animation_frame="Fecha", animation_group="Comuna", range_y=[-10,1500], hover_name='Comuna')
        simple_scatter.update_layout(margin={"r":0,"t":80,"l":0,"b":0}, title_text = "Caso Confirmados acumulados en el tiempo (escala logarítmica)")
        simple_scatter.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000


        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'double_scatter',
                                        figure = double_scatter,
                                        style = {'height':'80vh'}
                                        ), md=12))

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'tasa',
                                        figure = tasa,
                                        style = {'height':'80vh'}
                                        ), md=12))

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'simple_scatter',
                                        figure = simple_scatter,
                                        style = {'height':'80vh'}), md=12))



    if dataset_value == 'CC':

        df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosAcumuladosPorComuna.csv")
        if comuna_value != 0:
            df = df.loc[df['Codigo region'] == comuna_value]

        fig = go.Figure(go.Choroplethmapbox(geojson=geojson_comunas, locations=df.Comuna, z=df[df.columns[-2]],
                                    colorscale="Reds", zmin=0, zmax=100, showscale = False,
                                    marker_opacity=0.9, marker_line_width=0.01, featureidkey='properties.comuna'))
        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token, autosize = True)
        fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, title_text = f"Casos confirmados acumulados al {df.columns[-2]}")

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

        bar_fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, autosize = True)
        bar_fig.update_layout(title_text = f'Casos confirmados acumulados al {df.columns[-2]}| Top Comunas')

        graphs.append(dbc.Col(dcc.Graph(
                                        id='mapa',
                                        figure=fig,
                                        style={'height':'100vh'}
                                        ), md=6))
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'scatter',
                                        figure = bar_fig,
                                        style={'height':'100vh'}
                                        ), md=6))

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
        table.update_layout(margin={"r":10,"t":45,"l":0,"b":20}, height = 700, title = 'Zonas en Cuarentena')
        #table.update_layout(plot_bgcolor =plt_background, paper_bgcolor=plt_background)

        #quarentine map

        px.set_mapbox_access_token(token)
        map = px.scatter_mapbox(cuarentena_df, lat="latitude", lon="longitude",
                                size= 'Estado',size_max=40, zoom=2, text = 'Nombre')
        map.update_layout(mapbox_style = 'light',mapbox_zoom=3.1, mapbox_center = {"lat": -36.8, "lon": -73.5}, title_text='Mapa Cuarentena')
        map.update_layout(margin={"r":10,"t":45,"l":0,"b":0}, height = 700)
        #map.update_layout(plot_bgcolor =plt_background, paper_bgcolor=plt_background)

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'table',
                                        figure = table
                                        ), md=6))
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'mapa',
                                        figure = map
                                        ), md=6))

    if dataset_value == 'CA':
        df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/input/InformeEpidemiologico/CasosActualesPorComuna.csv")
        if comuna_value != 0:
            df = df.loc[df['Codigo region'] == comuna_value]
        fig = go.Figure(go.Choroplethmapbox(geojson=geojson_comunas, locations=df.Comuna, z=df[df.columns[-1]],
                                    colorscale="Reds", zmin=0, zmax=100, showscale = False,
                                    marker_opacity=0.9, marker_line_width=0.01, featureidkey='properties.comuna'))
        fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
        fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, height = 700, title_text= f'Mapa Casos activos al {df.columns[-1]}')
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

        bar_fig.update_layout(margin={"r":0,"t":45,"l":0,"b":0}, height=700)
        bar_fig.update_layout(title_text =f'Casos activos al {df.columns[-1]}| Top Comunas')
        if comuna_value != 0:
            bar_fig.update_layout(yaxis={'tickmode':'linear'})


        #appending
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'mapa',
                                        figure = fig,
                                        style = {'height':'100vh'}
                                        ),md=6))
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'scatter',
                                        figure = bar_fig,
                                        style = {'height':'100vh'}
                                        ), md=6))


    if  dataset_value == 'EP':

        #fallecidos
        facdf = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto14/FallecidosCumulativo.csv")
        facdf = facdf.melt(id_vars=['Region'],
                                      var_name='Fecha', value_name='Fallecidos')
        fig_fall = px.scatter(facdf, x='Fecha', y='Fallecidos', color ='Region', text='Region')
        fig_fall.update_traces(mode='markers+lines')
        fig_fall.update_traces(mode='markers+lines', hovertemplate=  '%{text}<br> %{y}<extra></extra>')
        fig_fall.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, title_text = "Fallecidos acumulativo por regiones", hovermode='x')

        #pacientes criticos
        criticos_df=pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto23/PacientesCriticos.csv")
        criticos_df = criticos_df.melt(id_vars="Casos", var_name ='Fecha', value_name ='Pacientes Críticos')

        fig_crit = go.Figure(
            data=(px.scatter(criticos_df, x='Fecha', y='Pacientes Críticos')
                 )
                            )
        fig_crit.update_traces( mode='markers+lines',hovertemplate=  'Críticos:<br>%{y}<extra></extra>')
        fig_crit.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, title_text = "Pacientes críticos", hovermode='x')

        #ventiladores
        ventiladores_df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto20/NumeroVentiladores.csv")
        ventiladores_df = ventiladores_df.melt(id_vars='Ventiladores', var_name='Fecha', value_name='Nro Ventiladores')
        fig_ven = px.scatter(ventiladores_df, x='Fecha', y='Nro Ventiladores', color ='Ventiladores', text ='Ventiladores')
        fig_ven.update_traces(mode='markers+lines', hovertemplate=  '%{text}<br> %{y}<extra></extra>')
        fig_ven.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, title_text = "Disponibilidad de ventiladores en Chile", hovermode ='x')

        #pacientes uci
        uci_df = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto8/UCI.csv")
        uci_df = uci_df.melt(id_vars=['Region', 'Codigo region', 'Poblacion'],
                                      var_name='Fecha', value_name='Pacientes UCI')
        fig_uci = px.line(uci_df, x='Fecha', y='Pacientes UCI', text ='Region', color = 'Region')
        fig_uci.update_traces(mode='markers+lines', hovertemplate=  '%{text}<br> %{y}<extra></extra>')
        fig_uci.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, title_text = "Pacientes en UCI por regiones", hovermode='x')

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_fall',
                                        figure = fig_fall,
                                        style = {'height':'60vh'}
                                        ), md=12))

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_crit',
                                        figure = fig_crit,
                                        style = {'height':'60vh'}
                                        ), md=12))
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_ven',
                                        figure = fig_ven,
                                        style = {'height':'60vh'}
                                        ), md=12))
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_uci',
                                        figure = fig_uci,
                                        style = {'height':'60vh'}
                                        ), md=12))

    if dataset_value == 'ES':
        #sintomas por casos confirmados
        sintomas_conf = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto21/SintomasCasosConfirmados.csv")
        fig_sc=(px.pie(sintomas_conf, values=sintomas_conf.columns[-1], names='Sintomas', title="Síntomas de casos confirmados",
            color_discrete_sequence =px.colors.sequential.RdBu))
        fig_sc.update_traces(textposition='inside', textinfo='label+percent', hovertemplate=None)

        sintomas_hosp = pd.read_csv("https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto21/SintomasHospitalizados.csv")
        fig_sh=(px.pie(sintomas_hosp, values=sintomas_hosp.columns[-1], names='Sintomas', title="Síntomas de pacientes hospitalizados",
            color_discrete_sequence =px.colors.sequential.RdBu))
        fig_sh.update_traces(textposition='inside', textinfo='label+percent', hovertemplate=None)

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_sc',
                                        figure = fig_sc,
                                        style = {'height':'60vh'}
                                        ), md=6))

        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_sh',
                                        figure = fig_sh,
                                        style = {'height':'60vh'}
                                        ), md=6))

    if dataset_value == 'MUND':
        import requests as rq
        #url of the api
        api = 'https://api.covid19api.com/summary'
        #requesting the data
        try:
            data = rq.get(api).json()
        except:
            try:
                data = rq.get(api).json()
            except:
                pass

        #defining the dataframe
        covid = pd.DataFrame(data['Countries'])
        #date to timestamp
        covid['Date'] =pd.to_datetime(covid['Date'])
        #getting the population data
        pop = pd.read_csv("data/population_by_country_2020.csv")
        #rename country column to math covid dataframe
        pop.rename(columns={'Country (or dependency)':'Country'}, inplace=True)

        #making the map
        text = [str(x)+ '<br>'+'Casos: '+str(f'{y:,}').replace(',','.') for x,y in zip(covid.Country,covid.TotalConfirmed)]


        fig_mundo = go.Figure(data=go.Choropleth(
            locations = covid.Country,
            z = np.log10(np.array(covid.TotalConfirmed)+1),
            text= text,
            hoverinfo='text',
            colorscale = 'hot_r',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'covid19<br>Total Confirmed',
            locationmode='country names',
            showscale=False
        ))

        fig_mundo.update_layout(
            margin={'t':30,'b':0,'r':0,'l':0},
            height=700,
            title_text=f'covid19: Confirmados totales en el mundo al {covid.Date.unique()[0].strftime("%d/%M/%Y")}',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
             )
        #     annotations = [dict(
        #         x=0.55,
        #         y=0.1,
        #         xref='paper',
        #         yref='paper',
        #         showarrow = False
        #     )]
        )

        #bar Figure
        covid = covid.dropna()
        covid = covid.sort_values(by='TotalConfirmed', ascending = True)
        fig_bar_world = go.Figure(data=(go.Bar(y = covid.Country, x=covid.TotalConfirmed,
                            text = covid.TotalConfirmed, orientation = 'h', textposition = 'outside')),
                            layout = (go.Layout(xaxis={'showgrid':False, 'ticks':'', 'showticklabels':False}, yaxis={'showgrid':False})))

        fig_bar_world.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=700)
        #fig_bar_world.update_layout(title_text =f'Casos activos al {df.columns[-1]}| Top Comunas')

        #appending
        graphs.append(dbc.Col(dcc.Graph(
                                        id = 'fig_mundo',
                                        figure = fig_mundo,
                                        style = {'height':'100vh'}
                                        ), md=12))
        #
        # graphs.append(html.Div(dcc.Graph(
        #                                 id = 'fig_bar_world',
        #                                 figure = fig_bar_world,
        #                                 style = {'height':'100vh'}
        #                                 ), className='col s12 m12 l4'))




    return graphs


if __name__ == '__main__':
    app.run_server(debug=True)
