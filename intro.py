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

provincia_abrev = ['A','AB','AL','AV','B','BA','BI','BU','C','CA','CC','CE','CO','CR','CS','CU','GC','GI','GR','GU','H','HU','J','L','LE','LO','LU','M','MA','ML','MU','NA','O','OR','P','PM','PO','S','SA','SE','SG','SO','SS','T','TE','TF','TO','V','VA','VI','Z','ZA']

provincia_incidencia = {'A':[],'AB':[],'AL':[],'AV':[],'B':[],'BA':[],'BI':[],'BU':[],'C':[],'CA':[],'CC':[],'CE':[],'CO':[],'CR':[],'CS':[],'CU':[],'GC':[],'GI':[],'GR':[],'GU':[],'H':[],'HU':[],'J':[],'L':[],'LE':[],'LO':[],'LU':[],'M':[],'MA':[],'ML':[],'MU':[],'NA':[],'O':[],'OR':[],'P':[],'PM':[],'PO':[],'S':[],'SA':[],'SE':[],'SG':[],'SO':[],'SS':[],'T':[],'TE':[],'TF':[],'TO':[],'V':[],'VA':[],'VI':[],'Z':[],'ZA':[]}

incidencia_vector = []

colors = {
'background': '#E2E8F5',
}

poblacion_prov = {'A':1879888,
'AB':388270,
'AL':727945,
'AV':157664,
'B':5743402,
'BA':672137,
'BI':1159543,
'BU':357650,
'C':1121815,
'CA':1244049,
'CC':391850,
'CE':84202,
'CO':781451,
'CR':495045,
'CS':585590,
'CU':196139,
'GC':1131065,
'GI':781788,
'GR':919168,
'GU':261995,
'H':524278,
'HU':222687,
'J':631381,
'L':438517,
'LE':456439,
'LO':319914,
'LU':327946,
'M':6779888,
'MA':1685920,
'ML':87076,
'MU':1511251,
'NA':661197,
'O':1018784,
'OR':306650,
'P':160321,
'PM':1171543,
'PO':945408,
'S':582905,
'SA':329245,
'SE':1950219,
'SG':153478,
'SO':88884,
'SS':727121,
'T':816772,
'TE':134176,
'TF':1044887,
'TO':703772,
'V':2591875,
'VA':520649,
'VI':1159443,
'Z':972528,
'ZA':170588}

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



for provincia in provincia_abrev:
    dff = df.copy()
    dff = dff[dff["provincia_iso"] == provincia]
    dff = dff.groupby('fecha').sum()
    date0 = datetime.now()
    catorce_dias = timedelta(days=14)
    contagios_catorce_dias = dff['num_casos'].loc[date0-catorce_dias:date0].sum()
    provincia_incidencia[provincia].append(contagios_catorce_dias/(poblacion_prov[provincia]/100000))
    incidencia_vector.append(contagios_catorce_dias/(poblacion_prov[provincia]/100000))

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(style={'backgroundColor': colors['background']},children=[

    html.H1("Análisis de la situación actual de la Covid-19 en España", style={'text-align': 'center', 'color':'black','font-family': 'Arial'}),

    html.Header(
        children = "Esta página web pretende mostrar la monitorización de la Covid-19 en España y en cada una de sus provincias",
        style = {
        "textAlign": "center",
        "color": "black",
        "fontSize": 25,
        "margin-top": "+18px"
        }
    ),

    html.Br(),

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

    dcc.Graph(id='incidencia_españa', figure={}),

    html.Br(),

#TO-DO Hay que comprobar que esten todas las provincias y bien puestas
    html.Div(
        children =[
    dcc.Dropdown(id="slct_prov",
                 options=[
                     {"label": "Álava", "value": 'VI'},
                     {"label": "Albacete", "value": 'AB'},
                     {"label": "Alicante", "value": 'A'},
                     {"label": "Almería", "value": 'AL'},
                     {"label": "Asturias", "value": 'O'},
                     {"label": "Ávila", "value": 'AV'},
                     {"label": "Badajoz", "value": 'BA'},
                     {"label": "Baleares", "value": 'PM'},
                     {"label": "Barcelona", "value": 'B'},           
                     {"label": "Burgos", "value": 'BU'},
                     {"label": "Cáceres", "value": 'CC'},
                     {"label": "Cádiz", "value": 'CA'},
                     {"label": "Cantabria", "value": 'S'},
                     {"label": "Castellón", "value": 'CS'},
                     {"label": "Ceuta", "value": 'CE'},
                     {"label": "Ciudad Real", "value": 'CR'},
                     {"label": "Córdoba", "value": 'CO'},
                     {"label": "Cuenca", "value": 'CU'},
                     {"label": "Guipúzcoa", "value": 'SS'},
                     {"label": "Girona", "value": 'GI'},
                     {"label": "Granada", "value": 'GR'},
                     {"label": "Gran Canaria", "value": 'GC'},
                     {"label": "Guadalajara", "value": 'GU'},
                     {"label": "Huelva", "value": 'H'},
                     {"label": "Huesca", "value": 'HU'},
                     {"label": "Jaén", "value": 'J'},
                     {"label": "La Coruña", "value": 'C'},
                     {"label": "La Rioja", "value": 'LO'},
                     {"label": "León", "value": 'LE'},
                     {"label": "Lleida", "value": 'L'},
                     {"label": "Lugo", "value": 'LU'},
                     {"label": "Madrid", "value": 'M'},
                     {"label": "Málaga", "value": 'MA'},
                     {"label": "Melilla", "value": 'ML'},
                     {"label": "Murcia", "value": 'MU'},
                     {"label": "Navarra", "value": 'NA'},
                     {"label": "Orense", "value": 'OR'},
                     {"label": "Palencia", "value": 'P'},
                     {"label": "Pontevedra", "value": 'PO'},
                     {"label": "Salamanca", "value": 'SA'},
                     {"label": "Segovia", "value": 'SG'},
                     {"label": "Sevilla", "value": 'SE'},
                     {"label": "Soria", "value": 'SO'},
                     {"label": "Tarragona", "value": 'T'},
                     {"label": "Tenerife", "value": 'TF'},
                     {"label": "Teruel", "value": 'TE'},
                     {"label": "Toledo", "value": 'TO'},
                     {"label": "Valencia", "value": 'V'},
                     {"label": "Valladolid", "value": 'VA'},
                     {"label": "Vizcaya", "value": 'BI'},
                     {"label": "Zamora", "value": 'ZA'},
                     {"label": "Zaragoza", "value": 'Z'}],
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
        ],
        style={'display':'flex','align-items':'center','justify-content':'center'}
    ),

    html.Div(id='output_container', children=[]),
    html.Br(),

	
    html.Div(children = [
        dcc.Graph(id='mapa_linea', figure={})
    ]
    ),
    html.Div(children = [
        html.Div( children = [
            html.P(
                children = "Incidencia acumulada",
                style = {
                    "textAlign":"center",
                    "color":"gray",
                    "fontSize":30
                }
            ),
            html.P(id = "incidencia",
                children = {},
                style = {
                    "textAlign":"center",
                    "color":"red",
                    "fontSize":20
                }
            )], style = {'width':'20%','display':'inline-block'}
        ),
        html.Div( children = [
            html.P(
                children = "Nuevos casos diagnosticados",
                style = {
                    "textAlign":"center",
                    "color":"gray",
                    "fontSize":30
                }
            ),
            html.P(
                id = 'nuevos_casos_provincia',
                children = {},
                style = {
                    "textAlign":"center",
                    "color":"red",
                    "fontSize":20
                }
            ) ], style = {'width':'20%','display':'inline-block'}
        ),
        html.Div( children = [
            html.P(
                children = "Nuevos casos en UCI",
                style = {
                    "textAlign":"center",
                    "color":"gray",
                    "fontSize":30
                }
            ),
            html.P(
                id = 'nuevos_uci_provincia',
                children = {},
                style = {
                    "textAlign":"center",
                    "color":"red",
                    "fontSize":20
                }
            )], style = {'width':'20%','display':'inline-block'}
        ),
        html.Div( children = [
            html.P(
                children = 'Nuevos fallecidos',
                style = {
                    "textAlign":"center",
                    "color":"gray",
                    "fontSize":30
                }
            ),
            html.P(
                id = 'nuevos_fallecidos_provincia',
                children = {},
                style = {
                    "textAlign":"center",
                    "color":"red",
                    "fontSize":20
                }
            )], style = {'width':'20%','display':'inline-block'}
        ),
        html.Div( children = [
            html.P(
                children = 'Nuevos casos hospitalizados',
                style = {
                    "textAlign":"center",
                    "color":"gray",
                    "fontSize":30
                } 
            ),
            html.P(
                id = 'nuevos_hosp_provincia',
                children = {},
                style = {
                    "textAlign":"center",
                    "color":"red",
                    "fontSize":20
                }
            ),
        ], style = {'width':'20%','display':'inline-block'})
    ], )

])



# ------------------------------------------------------------------------------
# Connect the Plotly graphs wirth Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='mapa_linea', component_property='figure'),
     Output(component_id='incidencia', component_property='children'),
     Output(component_id='incidencia_españa', component_property='figure'),
     Output(component_id='nuevos_casos_provincia', component_property='children'),
     Output(component_id='nuevos_uci_provincia', component_property='children'),
     Output(component_id='nuevos_fallecidos_provincia', component_property='children'),
     Output(component_id='nuevos_hosp_provincia', component_property='children'),],
    [Input(component_id='slct_prov', component_property='value'),
    Input(component_id='slct_tipo', component_property="value")]
)
def update_graph(slct_prov, slct_tipo):
    print(slct_prov)
    print(type(slct_prov))

    container = " " #He intentado quitar el output container pero da error, dejo un string vacío para que no se vea por pantalla

    incidencia_acumulada = round(provincia_incidencia[slct_prov][0])

    titulo_grafica = "{}".format(titulo[slct_tipo])

    dff = df.copy()
    dff = dff[dff['provincia_iso']==slct_prov]
    dff = dff.groupby('fecha').sum()
    nuevos_casos = dff['num_casos'].iloc[-1]
    nuevos_uci = dff['num_uci'].iloc[-1]
    nuevos_hopsitalizados = dff['num_hosp'].iloc[-1]
    nuevos_defunciones = dff['num_def'].iloc[-1]

    # Plotly Express
    fig = px.line(
        dff, y=slct_tipo, title=titulo_grafica
    )

    etiquetas = list(provincia_incidencia.keys())

    fig2 = go.Figure(
        [go.Bar(x = etiquetas, y = incidencia_vector)]
        
	)

    fig2.update_layout(title = 'Incidencia acumulada en España los últimos 14 días')
    
    return container, fig, incidencia_acumulada, fig2, nuevos_casos, nuevos_uci, nuevos_hopsitalizados, nuevos_defunciones


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)