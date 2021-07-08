
import streamlit as st
import pandas as pd

st.title("Heroku")
st.header("Exploracion")
st.markdown("Este dataset es un sample de 16.000 filas del dataset original")

data = pd.read_csv("data.csv")

#st.dataframe(data.head())
st.markdown("## Seleccionar las columnas a visualizar")
st_ms = st.multiselect("Atributos", data.columns.tolist(), default=["titulo","autor","posicion"])
st.dataframe(data.loc[:,st_ms])
st.markdown("## Seleccionar el rango de posiciones a visualizar")
pos_min,pos_max = st.slider("Posicion",data.posicion.min(),data.posicion.max(),(data.posicion.min(),data.posicion.max()))
st.dataframe(data[(data.posicion<=pos_max) & (data.posicion>=pos_min)])
