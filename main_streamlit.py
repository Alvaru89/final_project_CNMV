import streamlit as st
import SessionState
from  front_end.comparador_fondos_lean  import comp_fondos_web as cf
from  front_end.how_much import how_much as hm
# import front_end.top5_fondos as t5f

st.set_page_config(page_title="My API de fondos",layout='wide')
session_state = SessionState.get(a=0,fondos=[])
storage=[]
siteHeader = st.beta_container()
b1,b2,b3=st.beta_columns(3)
miniweb = st.beta_container()

PAGES = {"comparador_fondos": cf,
     "how_much": hm,
    # 'top5_fondos':t5f
         }

with siteHeader:
  st.title('Bienvenido a mi api de selección de fondos!')
  st.text('In this project...')

with b1:
  if st.button('Comparador de fondos') or session_state.a==1:
      session_state.a = 1
      with miniweb:
        PAGES["comparador_fondos"](storage)


with b2:
    if st.button('¿Cuanto habría ganado si...?') or session_state.a==2:
        session_state.a = 2
        with  miniweb:
            PAGES["how_much"]()


with b3:
    if st.button('Top 5 fondos'):
        # miniwebPAGES['top5_fondos']()
        pass