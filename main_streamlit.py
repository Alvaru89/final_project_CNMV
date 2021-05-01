import streamlit as st
import SessionState
from  front_end.home import home
from  front_end.comparador_fondos_lean  import comp_fondos_web as cf
from  front_end.how_much import how_much as hm
from front_end.top5_fondos import top5 as t5f

st.set_page_config(page_title="My API de fondos",layout='wide')
session_state = SessionState.get(a=0,fondos=[])
storage=[]
siteHeader = st.beta_container()
b0,b1,b2,b3=st.beta_columns(4)
miniweb = st.beta_container()
siteFooter = st.beta_container()

PAGES = {0: home,
    1: cf,
     2: hm,
     3:t5f }

with siteHeader:
  st.title('¡Bienvenido a FondoAdvisor! Tu api de selección de fondos de inversión.')

with b0:
  if st.button('Inicio'):
      session_state.a = 0

with b1:
  if st.button('Comparador de fondos'):
      session_state.a = 1


with b2:
    if st.button('¿Cuánto habría ganado si...?'):
        session_state.a = 2

with b3:
    if st.button('Top 5 fondos'):
        session_state.a = 3

with miniweb:
            PAGES[session_state.a]()

with siteFooter:
    style="""<style>
    a:link , a:visited{
    color: blue;
    background-color: transparent;
    text-decoration: underline;
    }

    a:hover,  a:active {
    color: red;
    background-color: transparent;
    text-decoration: underline;
    }

    .footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    color: black;
    text-align: center;
    }
    </style>"""
    footer = """
    <div    class ="footer">
    <p><small>
    Esta web ha sido desarrollada con Python y Streamlit.
    La información aquí publicada ha sido extraída o generada a partir de información pública de la Comisión Nacional de Mercado de Valores (CNMV) <a href="www.cnmv.es" target="_blank">link</a>.</small></p>
    </div>
    """
    st.markdown(style, unsafe_allow_html=True)
    st.markdown(footer, unsafe_allow_html=True)
    #
    #