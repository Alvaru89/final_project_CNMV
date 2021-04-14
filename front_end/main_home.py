import streamlit as st
import comparador_fondos

siteHeader = st.beta_container()
tools = st.beta_container()

with siteHeader:
  st.title('Bienvenido a mi api de selección de fondos!')
  st.text('In this project...')
with tools:
  if st.button('Comparador de fondos')
      comparador_fondos
with newFeatures:
  st.header('New features I came up with')
  st.text('Let\'s take a look into the features I generated.')
with modelTraining:
  st.header('Model training')
 st.text('In this section you can select the hyperparameters!')