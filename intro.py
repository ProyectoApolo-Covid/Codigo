import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# ---------- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
path = '/home/juanda/Documents/BioInf/Python/py_industriales_2021-main/covid/casos_hosp_uci_def_sexo_edad_provres.csv'
df = pd.read_csv(path, delimiter=',', parse_dates=['fecha'], index_col='fecha')
print(df)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),
#Hay que comprobar que esten todas las provincias y bien puestas
    dcc.Dropdown(id="slct_year",
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
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The provincia chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["provincia_iso"] == option_slctd]
    dff = dff.groupby('fecha').sum()
    print(dff)

    # Plotly Express
    fig = px.line(
        dff, y='num_casos', title='Holamundo'
    )

    # Plotly Graph Objects (GO)
    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Reds',
    #     )]
    # )
    #
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)