import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import requests
from pathlib import Path
import numpy as np
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from plotly.graph_objs import *

URL_ISCIII = 'https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres.csv'
BASE_DIR = Path()
CACHE_DIR = BASE_DIR / 'cache'
CACHE_DIR.mkdir(exist_ok=True)
ORIG_DATE_COL = 'fecha'
ORIG_CASES_COL = 'num_casos'
ORIG_HOSP_COL = 'num_hosp'
ORIG_UCI_COL = 'num_uci'
ORIG_DEF_COL = 'num_def'
DATA_COLS = [ORIG_CASES_COL, ORIG_HOSP_COL, ORIG_UCI_COL, ORIG_DEF_COL]
PROV_ISO_COL = 'provincia_iso'

EVOLUTION_PLOTS_DIR = BASE_DIR / 'evolutions'

def download_iscii_data():
    fname = URL_ISCIII.split('/')[-1]
    now = datetime.now()
    
    fname = f'{now.year}_{now.month}_{now.day}_{fname}'
    path = CACHE_DIR / fname
    
    if path.exists():
        return path
    
    response = requests.get(URL_ISCIII)
    
    if response.status_code != 200:
        raise RuntimeError(f'Error downloading file: {URL_ISCIII}')
    
    fhand = path.open('wb')
    for chunk in response.iter_content(chunk_size=128):
        fhand.write(chunk)
    
    return path


def get_dframe(date_range=None):
    
    path = download_iscii_data()
    
    dframe = pd.read_csv(path, header=0,
                             parse_dates=[ORIG_DATE_COL])
    
    if date_range is not None:
        mask = np.logical_and(dframe[ORIG_DATE_COL] >= date_range[0],
                                 dframe[ORIG_DATE_COL] <= date_range[1])
        dframe = dframe.loc[mask, :]
    
    return dframe


app = dash.Dash(__name__,meta_tags = [{"name": "viewport", "content": "width=device-width"}])

#Leemos el csv con los datos (luego cambiare a que descargue automáticamente el más nuevo)
df = get_dframe()
print(df)
titulo = {'num_casos':'Número de casos', 'num_hosp':'Número de hospitalizaciones',
'num_def':'Número de fallecidos','num_uci':'Número de pacientes en la UCI'}

#Algunos datos que cojo aparte de una página de estadisticas
url_data_dia = "https://covid-193.p.rapidapi.com/statistics"
querystring = {"country":"Spain"}
headers = {
    'x-rapidapi-host': "covid-193.p.rapidapi.com",
    'x-rapidapi-key': "be7f37114bmsh38c0486c35a5050p1bc1e5jsnf574155ad041"
}
response = requests.request("GET", url_data_dia, headers=headers, params=querystring).json() #Leemos el json 
data = response['response']
data = data[0]
#Nos quedamos los casos activos y las camas de UCI ocupadas
info_actual = {
    'activos': data['cases']['active'],
    'ucis': data['cases']['critical'],
}

dfinfo = df.groupby('fecha').sum()
num_casos_nuevos = dfinfo['num_casos'].iloc[-1] #Casos nuevos
num_casos_totales = dfinfo['num_casos'].sum() #Casos totales
num_uci_nuevos = dfinfo['num_uci'].iloc[-1] #Casos nuevos UCI
num_def_nuevos = dfinfo['num_def'].iloc[-1] #Muertes nuevas
num_def_totales = dfinfo['num_def'].sum() #Muertes totales
num_casos_curados = num_casos_totales - info_actual['activos']
incidencia_acumulada = 0

#Calculo de la incidencia acumulada
date0 = datetime.now()
un_dia_menos = timedelta(days=2) #Damos un poco de margen por si el ultimo dia todavia no esta registrado en el csv
date0 = date0 - un_dia_menos
catroce_dias = timedelta(days=14)
contagios_catorce_dias = dfinfo['num_casos'].loc[date0-catroce_dias:date0].sum()
incidencia_acumulada = contagios_catorce_dias/(47332614/100000)


# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(children=[

    html.H1("Análisis de la situacion actual del Covid-19 en España", style={'text-align': 'center', 'color':'gray'}, ),

    html.Div(
			children = [
				# (Columna 1): Contagios totales
				html.Div(
					children = [
						# Título
						html.H6(
							children = "Contagios de COVID-19",
							style = {
								"textAlign": "center",
								"color": "gray",
                                "fontSize": 25,
                                "margin-top": "+18px"
							}
						),
						# Número total
						html.P(
							children = num_casos_totales,
							style = {
								"textAlign": "center",
								"color": "#dd1e35",
								"fontSize": 40,
                                "margin-top": "-30px"
							}
						),
						# Nuevos casos
						html.P(
							children = 'Nuevos: +' + str(num_casos_nuevos) ,
							style = {
								"textAlign": "center",
								"color": "#59BE13",
								"fontSize": 15,
								"margin-top": "-18px"
							}
						)
					],
                    style = {'width':'25%','display':'inline-block'},
					className = "card_container three columns"
				),
				# (Columna 2): Casos activos
				html.Div(
					children = [
						# Título
						html.H6(
							children = "Casos activos",
							style = {
								"textAlign": "center",
								"color": "gray",
								"fontSize":25,
								"margin-top": "+18px"
							}
						),
						# Número total
						html.P(
							children = info_actual['activos'],
							style = {
								"textAlign": "center",
								"color": "#dd1e35",
								"fontSize": 40,
								"margin-top": "-30px"
							}
						),
						# Casos nuevos
						html.P(
							children = "Nuevos: +" + str(num_casos_nuevos) ,
							style = {
								"textAlign": "center",
								"color": "#59BE13",
								"fontSize": 15,
								"margin-top": "-18px"
							}
						)
					],
                    style = {'width':'25%','display':'inline-block'},
					className = "card_container three columns"
				),
				# (Columna 3): UCIs ocupadas
				html.Div(
					children = [
						# Título
						html.H6(
							children = "UCIs ocupadas",
							style = {
								"textAlign": "center",
								"color": "gray",
								"fontSize":25,
								"margin-top": "+18px"
							}
						),
						# Número de UCIs ocupadas
						html.P(
							children = info_actual['ucis'],
							style = {
								"textAlign": "center",
								"color": "#dd1e35",
								"fontSize": 40,
								"margin-top": "-30px"
							}
						),
						# Nuevas UCIs ocupadas
						html.P(
							children = "Nuevos: +" + str(num_uci_nuevos),
							style = {
								"textAlign": "center",
								"color": "#59BE13",
								"fontSize": 15,
								"margin-top": "-18px"
							}
						)
					],
                    style = {'width':'25%','display':'inline-block'},
					className = "card_container three columns"
				),
				# (Columna 4): Fallecidos
				html.Div(
					children = [
						# Título
						html.H6(
							children = "Número de fallecidos",
							style = {
								"textAlign": "center",
								"color": "gray",
								"fontSize":25,
								"margin-top": "+18px"
							}
						),
						# Total fallecidos
						html.P(
							children = num_def_totales,
							style = {
								"textAlign": "center",
								"color": "#dd1e35",
								"fontSize": 40,
								"margin-top": "-30px"
							}
						),
						# Nuevos fallecidos
						html.P(
							children = "Nuevos: +" + str(num_def_nuevos),
							style = {
								"textAlign": "center",
								"color": "#59BE13",
								"fontSize": 15,
								"margin-top": "-18px"
							}
						)
					],
                    style = {'width':'25%','display':'inline-block'},
					className = "card_container three columns"
				)
			],
			className = "row flex-display"
		),

#TO-DO Hay que comprobar que esten todas las provincias y bien puestas
    dcc.Dropdown(id="slct_mes",
                 options=[
                     {"label": "Alicante", "value": 'A'},
                     {"label": "Albacete", "value": 'AB'},
                     {"label": "Almería", "value": 'AL'},
                     {"label": "Ávila", "value": 'AV'},
                     {"label": "Barcelona", "value": 'B'},
                     {"label": "Badajoz", "value": 'BA'},
                     {"label": "Bilbao", "value": 'BI'},
                     {"label": "Burgos", "value": 'BU'},
                     {"label": "La Coruña", "value": 'C'},
                     {"label": "Cádiz", "value": 'CA'},
                     {"label": "Cáceres", "value": 'CC'},
                     {"label": "Ceuta", "value": 'CE'},
                     {"label": "Córdoba", "value": 'CO'},
                     {"label": "Ciudad Real", "value": 'CR'},
                     {"label": "Castellón", "value": 'CS'},
                     {"label": "Cuenca", "value": 'CU'},
                     {"label": "Gran Canaria", "value": 'GC'},
                     {"label": "Girona", "value": 'GI'},
                     {"label": "Granada", "value": 'GR'},
                     {"label": "Guadalajara", "value": 'GU'},
                     {"label": "Huelva", "value": 'H'},
                     {"label": "Huesca", "value": 'HU'},
                     {"label": "Jaén", "value": 'J'},
                     {"label": "Lleida", "value": 'L'},
                     {"label": "León", "value": 'LE'},
                     {"label": "La Rioja", "value": 'LO'},
                     {"label": "Lugo", "value": 'LU'},
                     {"label": "Madrid", "value": 'M'},
                     {"label": "Málaga", "value": 'MA'},
                     {"label": "Melilla", "value": 'ML'},
                     {"label": "Murcia", "value": 'MU'},
                     {"label": "Navarra", "value": 'NA'},
                     {"label": "Asturias", "value": 'O'},
                     {"label": "Orense", "value": 'OR'},
                     {"label": "Palencia", "value": 'P'},
                     {"label": "Islas Baleares", "value": 'PM'},
                     {"label": "Pontevedra", "value": 'PO'},
                     {"label": "Cantabria", "value": 'S'},
                     {"label": "Salamanca", "value": 'SA'},
                     {"label": "Sevilla", "value": 'SE'},
                     {"label": "Segovia", "value": 'SG'},
                     {"label": "Soria", "value": 'SO'},
                     {"label": "Guipúzcoa", "value": 'SS'},
                     {"label": "Tarragona", "value": 'T'},
                     {"label": "Teruel", "value": 'TE'},
                     {"label": "Tenerife", "value": 'TF'},
                     {"label": "Toledo", "value": 'TO'},
                     {"label": "Valencia", "value": 'V'},
                     {"label": "Valladolid", "value": 'VA'},
                     {"label": "Vizcaya", "value": 'VI'},
                     {"label": "Zaragoza", "value": 'Z'},
                     {"label": "Zamora", "value": 'ZA'}],
                 multi=False,
                 value='A',
                 style={'width': "50%"}
                 ),
    
    dcc.Dropdown(id="slct_tipo",
                 options=[
                     {"label": "Número de casos totales", "value": 'num_casos'},
                     {"label": "Número de casos en UCI", "value": 'num_uci'},
                     {"label": "Número de fallecidos", "value": 'num_def'},
                     {"label": "Número de hospitalizados", "value": 'num_hosp'}],
                 multi=False,
                 value='num_casos',
                 style={'width': "50%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

	html.Div(children=[
		html.Div(children = [
			dcc.Graph(id='mapa_linea', figure={})
		], 	style={'width':'33%','display':'inline-block'},
		),
		html.Div(children=[
			dcc.Graph(id='tarta', figure={})
		], 	style={'width':'33%','display':'inline-block'},
		),
		html.Div(children=[
			html.H6(
				children = "Incidencia acumulada",
				style = {
					"textAlign":"center",
					"color":"gray",
					"fontSize":40
				}
			),
			html.P(
				children = incidencia_acumulada,
				style = {
					"textAlign":"center",
					"color":"red",
					"fontSize":20
				}
			)
		], style={"width":"33%","display":"inline-block"})
	],
	className='card_container three columns'
	),
] )


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='mapa_linea', component_property='figure'),
	 Output(component_id='tarta', component_property='figure')],
    [Input(component_id='slct_mes', component_property='value'),
    Input(component_id='slct_tipo', component_property="value")]
)
def update_graph(slct_mes, slct_tipo):
    print(slct_mes)
    print(type(slct_mes))

    container = " " #He intentado quitar el output container pero da error, dejo un string vacío para que no se vea por pantalla

    data_pie = [num_casos_totales,num_casos_curados,info_actual['activos'],num_def_totales] #He intentado quitar el output container pero da error, dejo un string vacío para que no se vea por pantalla

    dff = df.copy()
    dff = dff[dff["provincia_iso"] == slct_mes]
    dff = dff.groupby('fecha').sum()
    print(dff)
    titulo_grafica = "{}".format(titulo[slct_tipo])

    # Plotly Express
    fig = px.line(
        dff, y=slct_tipo, title=titulo_grafica
    )

    fig2 = go.Figure(
        data=[go.Pie(labels=['Confirmados','Curados','Activos', 'Fallecidos'], values=data_pie)]
	)

    
    return container, fig, fig2


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)