import streamlit as st

def home():
    st.markdown('''
        El propósito de esta web es ayudar a inversores (actuales o futuros) a elegir el mejor fondo de inversión.

        Con datos de más de 1200 fondos extraídos de la Comisión Nacional del Mercado de Valores (CNMV), puedes utilizar las siguientes herramientas: 

        - **_Comparador de fondos_**: es una herramienta para poder comparar varias variables financieras 

        - **_¿Cuánto habría ganado si...?_**: permite calcular el valor actual de un hipotética inversión en un fondo.

        - **_Top 5 fondos_**: permite consultar los fondos con mejores rentabilidad por periodo. Por favor, se paciente ya que requiere 2-3 minutos para cargar toda la base de datos.

        Espero que te sea de mucha ayuda y recuerda *'rentabilidades pasadas no garantizan rentabilidades futuras'*.

        ''')