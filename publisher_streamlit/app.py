
import streamlit as st
import pandas as pd
import os

filename = 'data.csv'
#dir = os.path.dirname(__file__)
#path = os.path.join(dir, filename)
path = os.sep.join([self.root, filename])

data = pd.read_csv(path).convert_dtypes()

st.title("Heroku")
st.header("Exploracion")
st.markdown("Este dataset es un sample de 16.000 filas del dataset original")

st.markdown("## Seleccionar las columnas a visualizar")
st_ms = st.multiselect("Atributos", data.columns.tolist(), default=["titulo","autor","posicion"])
st.dataframe(data.loc[:,st_ms])
st.markdown("## Seleccionar el rango de posiciones a visualizar")

pos_min,pos_max = data.posicion.min().item(),data.posicion.max().item()
user_min,user_max = st.slider("Posicion",pos_min,pos_max,(pos_min,pos_max))
st.dataframe(data[(data.posicion<=user_max) & (data.posicion>=user_min)])
