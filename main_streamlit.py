import streamlit as st
from  front_end.comparador_fondos  import comp_fondos_web as cf
# import front_end.how_much as hm
# import front_end.top5_fondos as t5f

siteHeader = st.beta_container()
b1,b2,b3=st.beta_columns(3)
miniweb = st.beta_container()

PAGES = {"comparador_fondos": cf,
    # "how_much": hm,
    # 'top5_fondos':t5f
         }

with siteHeader:
  st.title('Bienvenido a mi api de selección de fondos!')
  st.text('In this project...')

with b1:
  if st.button('Comparador de fondos'):
    miniweb.PAGES["comparador_fondos"]()

with b2:
    if st.button('¿Cuanto habría ganado si...?'):
        # miniweb=PAGES["how_much"]()
        pass

with b3:
    if st.button('Top 5 fondos'):
        # miniwebPAGES['top5_fondos']()
        pass