from pathlib import Path 
import matplotlib
import datetime
import numpy as np 
import pandas as pd 

ruta = Path.home() / 'OneDrive' / 'Documentos' / 'CUARTO GIB' / 'Bioinformatica' / 'jose blanca' / 'py_industriales_2021-main' / 'covid' / 'casos_covid_actualizados.csv'
dframe = pd.read_csv(ruta,parse_dates=['fecha'],index_col=['fecha'])
num_uci = dframe['num_uci']

# vamos a sacar el número de ingresos en uci por día en todas las provincias

num_uci_por_dia = num_uci.groupby(by='fecha').sum()
#print(num_uci_por_dia)
# para sacar el máximo en un día
#print(num_uci_por_dia.max())
# si lo queremos calcular por semanas, ya que los fines de semana no se suelen publicar muchos datos
num_uci_por_semana = num_uci_por_dia.resample('7D').sum()
#print(num_uci_por_semana)

# para obtener este dato por provincias

num_uci_por_provincia = dframe.loc[:,('provincia_iso','num_uci')].groupby('provincia_iso').sum()
print(num_uci_por_provincia)
num_casos_por_provincia.plot.bar()

# si queremos indicar fechas

ultimo_dia = datetime.datetime.now()
un_mes = datetime.timedelta(days=30)
primer_dia = ultimo_dia - un_mes
num_uci_por_prov_un_mes = dframe.loc[primer_dia:ultimo_dia,('provincia_iso','num_uci')].groupby('provincia_iso').sum()
print(num_uci_por_prov_un_mes)
num_uci_por_prov_un_mes.plot()

#para el numero de casos
num_casos= dframe['num_casos']

num_casos_por_dia= num_casos.groupby(by='fecha').sum()
num_casos_por_semana= num_casos_por_dia.resample('7D').sum()
#en las provincias
num_casos_por_provincia = dframe.loc[:,('provincia_iso','num_casos')].groupby('provincia_iso').sum()



