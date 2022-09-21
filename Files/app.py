import streamlit as st
import requests
import pandas as pd
import datetime as dt
from sodapy import Socrata
from scipy.signal import argrelextrema
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.offline as po
import plotly.graph_objs as pg
import plotly.express as px


#client = Socrata("healthdata.gov", None)
#results = client.get("g62h-syeh", limit=50000)
#df = pd.DataFrame.from_records(results)

df = pd.read_csv(r"D:\Henry\PI 2\my_table.csv") #importar desde CSV si no funciona la API

df["date"] = pd.to_datetime(df["date"])
df.sort_values(by="date", inplace=True)
df.reset_index(inplace=True)
df.drop(columns="index",axis=1, inplace=True)

df=df[(df.date>="2020-01-01") & (df.date<="2022-08-01")]

df.fillna(0, inplace=True)

df = df.astype({"inpatient_beds_used_covid" :int, "staffed_adult_icu_bed_occupancy" :int, "staffed_pediatric_icu_bed_occupancy":int,
"staffed_icu_pediatric_patients_confirmed_covid" :int, "staffed_icu_adult_patients_confirmed_covid" :int, "total_pediatric_patients_hospitalized_confirmed_covid" :int,
"deaths_covid" :int})

df["Ocupación_Total_ICU"] = df.staffed_adult_icu_bed_occupancy+df.staffed_pediatric_icu_bed_occupancy
df["Total_Confirmados_ICU"] = df.staffed_icu_adult_patients_confirmed_covid+df.staffed_icu_pediatric_patients_confirmed_covid
df['Año'] = pd.DatetimeIndex(df['date']).year
df["Mes"] = df.date.dt.strftime('%mm')
df["Año_Mes"] = df["Año"].astype(str)+ "-" +df["Mes"].astype(str)


st.header("Proyecto Individual 2")
st.header("Ramseyer, Franco")

#MAPA 1 ) OCUPACIÓN HOSPITALARIA POR COVID

mapa_1 = df.groupby("state").sum("inpatient_beds_used_covid")["inpatient_beds_used_covid"].to_frame()

data1=dict(type = "choropleth", 
 locations = mapa_1.index, 
 locationmode = "USA-states", 
 z = mapa_1["inpatient_beds_used_covid"])

layout1 = dict(title = 'Ocupación de camas por COVID por Estado', title_x=0.5, title_font_size=30, geo = {'scope':'usa'})
x1 = pg.Figure(data=[data1],
layout = layout1)
x1.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'))
st.write(x1)

#MAPA 2 ) USO DE CAMAS UCI POR ESTADO

mapa_2 = df.groupby("state").sum("Ocupación_Total_ICU")["Ocupación_Total_ICU"].to_frame()

data2=dict(type = "choropleth", 
 locations = mapa_2.index, 
 locationmode = "USA-states", 
 z = mapa_2["Ocupación_Total_ICU"])

layout2 = dict(title = 'Ocupación de camas UCI por Estado', title_x=0.5, title_font_size=30, geo = {'scope':'usa'})
x2 = pg.Figure(data = [data2] ,
layout = layout2)
x2.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'))
st.write(x2)

#SLIDER

st.subheader("Calculadora de camas ocupadas por COVID")

fecha_inicio, fecha_fin = st.date_input('Fecha inicio  - fecha fin :', [])
if fecha_inicio < fecha_fin:
    if str(fecha_inicio)>="2020-01-01" and str(fecha_fin)<="2022-08-01":
        mascara = df[(df['date'] >= str(fecha_inicio)) & (df['date'] <= str(fecha_fin))]

        st.write("La cantidad de camas ocupadas por COVID-19 en Estados Unidos fue de",
        round(sum(mascara.inpatient_beds_used_covid)/1000000,2), "millones")
    
    else:    
        st.error('Error: Las fechas deben estar entre el 01/01/2020 y 01/08/2022.')
else: st.error("La fecha de inicio debe ser previa a la fecha de fin")



# 1 - ¿Cuáles fueron los 5 Estados con mayor ocupación hospitalaria por COVID? 

df_6m = df[(df.date>="2020-01-01") & (df.date<="2020-06-30")]

Frame_1 = df_6m.groupby("state").sum("inpatient_beds_used_covid").sort_values("inpatient_beds_used_covid", ascending=False)["inpatient_beds_used_covid"].head().to_frame()

st.subheader("1) Estados con mayor ocupación hospitalaria por COVID (1° semestre 2020)")
fig1_1=px.bar(Frame_1)
fig1_1.update_yaxes(title="", visible=True)
fig1_1.update_xaxes(title="Estado", visible=True)
fig1_1.update_layout(showlegend=False)
st.write(fig1_1)


#2 Analice la ocupación de camas (Común) por COVID en el Estado de Nueva York durante la cuarentena establecida e indique:

#Intervalos de crecimiento y decrecimiento
#Puntos críticos (mínimos y máximos)

st.subheader("2) Ocupación de camas en el estado de Nueva York durante la cuarentena")

df_cuarentena_NY = df[(df.date>="2020-03-01") & (df.date<="2021-06-30") & (df.state == "NY")]

df_cuarentena_NY.set_index("date", inplace=True)

df_cuarentena_NY_mins = df_cuarentena_NY.iloc[argrelextrema(df_cuarentena_NY.inpatient_beds_used_covid.values, np.less_equal,
                    order=100)[0]]['inpatient_beds_used_covid']
df_cuarentena_NY_maxs = df_cuarentena_NY.iloc[argrelextrema(df_cuarentena_NY.inpatient_beds_used_covid.values, np.greater_equal,
                    order=100)[0]]['inpatient_beds_used_covid']


fig1=px.line(x= df_cuarentena_NY.index, y=df_cuarentena_NY.inpatient_beds_used_covid)
fig2=px.scatter(x=df_cuarentena_NY_mins.index, y=df_cuarentena_NY_mins, color_discrete_sequence=["red"])
fig2.update_traces(marker={'size': 12})
fig3=px.scatter(x=df_cuarentena_NY_maxs.index, y=df_cuarentena_NY_maxs, color_discrete_sequence=["green"])
fig3.update_traces(marker={'size': 12})
fig4=pg.Figure(data=fig1.data + fig2.data + fig3.data, layout_title_text='Ocupación de camas por pacientes con COVID en el estado de Nueva York',
layout_title_font_color="white", layout_title_font_size=17)
st.write(fig4)


st.write("Los intervalos de crecimiento fueron: \n", "* Desde", df_cuarentena_NY_mins.index[0].date(), "hasta", df_cuarentena_NY_maxs.index[0].date(),
"\n * Desde", df_cuarentena_NY_mins.index[1].date(), "hasta", df_cuarentena_NY_maxs.index[1].date())
st.write("\n Los intervalos de decrecimiento fueron: \n", "* Desde", df_cuarentena_NY_maxs.index[0].date(), "hasta", df_cuarentena_NY_mins.index[1].date(),
"\n * Desde", df_cuarentena_NY_maxs.index[1].date(), "hasta", df_cuarentena_NY_mins.index[2].date())


#Comportamiento cíclico

st.subheader("Comportamiento cíclico")

df_NY_CA_TX_FL = df[(df.state == "NY")|(df.state == "CA")|(df.state == "TX")|(df.state == "FL")]
FigCiclo = px.line(x= df_NY_CA_TX_FL["date"], y=df_NY_CA_TX_FL["inpatient_beds_used_covid"], line_group=df_NY_CA_TX_FL.state, color=df_NY_CA_TX_FL.state)
FigCiclo.update_yaxes(title="", visible=True)
FigCiclo.update_xaxes(title="", visible=True)
st.write(FigCiclo)

# 3 - ¿Cuáles fueron los cinco Estados que más camas UCI -Unidades de Cuidados Intensivos- 

df_2020 = df[(df.date>="2020-01-01") & (df.date<="2020-12-31")]
Frame_3 = df_2020.groupby("state").sum("Ocupación_Total_ICU").sort_values("Ocupación_Total_ICU", ascending=False)["Ocupación_Total_ICU"].to_frame().head()


st.subheader("3) Estados con mayor ocupación de camas UCI (año 2020)")

fig3_1=px.bar(Frame_3)
fig3_1.update_yaxes(title="", visible=True)
fig3_1.update_xaxes(title="Estado", visible=True)
fig3_1.update_layout(showlegend=False)
st.write(fig3_1)


# 4 - ¿Qué cantidad de camas se utilizaron, por Estado, para pacientes pediátricos con COVID durante el 2020?

Frame_4 = df_2020.groupby("state").sum("total_pediatric_patients_hospitalized_confirmed_covid").sort_values("total_pediatric_patients_hospitalized_confirmed_covid", ascending=False)["total_pediatric_patients_hospitalized_confirmed_covid"].to_frame()

st.subheader("4) Cantidad de camas utilizadas por pacientes pediátricos con COVID (año 2020)")

fig4_1=px.bar(Frame_4)
fig4_1.update_yaxes(title="", visible=True)
fig4_1.update_xaxes(title="Estado", visible=True)
fig4_1.update_layout(showlegend=False)
st.write(fig4_1)

# 5 - ¿Qué porcentaje de camas UCI corresponden a casos confirmados de COVID-19? Agrupe por Estado.

confirmados_porestado = df.groupby("state").sum("Total_Confirmados_ICU").sort_values("state")["Total_Confirmados_ICU"].to_frame()
ICU_porestado = df.groupby("state").sum("Ocupación_Total_ICU").sort_values("state")["Ocupación_Total_ICU"].to_frame()
ICU_porestado = pd.merge(confirmados_porestado, ICU_porestado, how="inner", on="state")
ICU_porestado["%_covid"]=ICU_porestado["Total_Confirmados_ICU"]/ICU_porestado["Ocupación_Total_ICU"]
Frame_5 = ICU_porestado.sort_values("%_covid", ascending=False)["%_covid"].to_frame()

st.subheader("5) Porcentaje de camas UCI que corresponden a casos confirmados de COVID-19") 

fig5_1=px.bar(Frame_5)
fig5_1.update_yaxes(title="", visible=True)
fig5_1.update_xaxes(title="Estado", visible=True)
fig5_1.update_layout(showlegend=False)
st.write(fig5_1)


# 6 - ¿Cuántas muertes por covid hubo, por Estado, durante el año 2021?

df_2021 = df[(df.date>="2021-01-01") & (df.date<="2021-12-31")]
Frame_6 = df_2021.groupby("state").sum("deaths_covid").sort_values("deaths_covid", ascending=False)["deaths_covid"].to_frame()

st.subheader("Muertes por COVID por Estado (año 2021)")

fig6_1=px.bar(Frame_6)
fig6_1.update_yaxes(title="", visible=True)
fig6_1.update_xaxes(title="Estado", visible=True)
fig6_1.update_layout(showlegend=False)
st.write(fig6_1)

# 8) Peor mes de la pandemia. Me baso en un criterio de muertes por mes

st.subheader("Muertes mensuales por COVID en Estados Unidos")

muertes_mensuales=df.groupby("Año_Mes").sum("deaths_covid")
fig8_1= px.line(x=muertes_mensuales.index, y=muertes_mensuales.deaths_covid)
fig8_1.update_yaxes(title="", visible=True, showgrid=False)
fig8_1.update_xaxes(title="Estado", visible=True, showgrid=False)
fig8_1.update_layout(showlegend=False)
st.write(fig8_1)

