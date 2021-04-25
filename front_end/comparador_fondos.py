import datetime
import streamlit as st
from p_wrangling.m_wrangling import wrang_main,load_fondo
import altair as alt
import os
import pandas as pd

def comp_fondos_web(final_fondo_sel):
  selection_col, display_col = st.beta_columns([1, 3])

  with selection_col:
    # st.header('Comparador de fondos')
    # st.text('Cargando base de datos')
    global storage
    path = 'data/csv'
    fondo_list=[file.split('.csv')[0] for file in os.listdir(path)]
    fondo_list.sort()
    #buscador de fondos
    input_text = st.text_input('Escribe aqui el fondo')

    if input_text:
      storage = final_fondo_sel
      output = [x for x in fondo_list if input_text.lower() in x.lower()]
      fondos_selected = st.multiselect("Elige fondos a comparar", output)
      final_fondo_sel +=fondos_selected
    else:
      fondos_selected = st.multiselect("Elige fondos a comparar", fondo_list)
      final_fondo_sel +=fondos_selected
      storage = final_fondo_sel

    data=''
    data_clean=''
    info_filtered = ''
    for fondo in final_fondo_sel:
        if len(data)==0:
            data=load_fondo(fondo,path)
            data_clean = wrang_main(data)
        else:
          data=pd.concat([data,load_fondo(fondo,path)])
          data_clean = wrang_main(data)

    # if st.button("Borrar selección de fondos"):
    #   final_fondo_sel=[]

    if len(data)>0:
      year_start=int(data_clean.year.min()) #ver minimo del dataframe
    else: year_start=2000
    if len(data)>0:
      year_end = int(data_clean.year.max())  # ver minimo del dataframe
    else: year_end=datetime.date.today().year
    input_years = st.slider("Años", year_start, year_end, (year_start, year_end), 1)
    y1,y2=input_years
    input_period = selection_col.selectbox('Periodo/Frecuencia a visualizar',
                                           options=['Trimester','Semester','Year'], index=0)

    vars_list=['rentab_avg','rotacion',
              'n_participaciones', 'n_participes',
              'beneficio', 'patrimonio',
               'valor_liq',
              'comision_gest_total', #'comision_depos',
              'rentab_IIC_trim',
              'volat_vl_trim', 'ratio_gastos_trim']

    input_vars = st.multiselect('¿Qué variables te gustaría comparar? (Máximo recomendado 3)', vars_list, ['rentab_avg'])

    #creating data for viz
    if len(data)>0:
      mask_years=(data_clean['year']>y1)&(data_clean['year']<y2)
      mask_period=data_clean['period_type']==input_period[0]   #!!!!!! revisar esto con nuevo periodo
      data_filtered = data_clean[mask_years & mask_period]
      data_filtered.sort_values('end_date', ascending=True, inplace=True)

      for fondo in final_fondo_sel:
        mask1 = data_clean['fondo'] == fondo
        last_date=data_clean[mask1].end_date.max()
        mask2=data_clean['end_date']==last_date
        if len(info_filtered)==0:
          info_filtered=data_clean[mask1&mask2]
        else:
          info_filtered=pd.concat([info_filtered,data_clean[mask1&mask2]])

  with display_col:
    info_expander = st.beta_expander(f"Info general de los fondos")
    graphs = st.beta_container()

    with info_expander:   #ultima info disponible fondo
        st.text(f'Fondos seleccionados: {final_fondo_sel}')
        if 'ACCION IBEX 35 ETF, FI COTIZADO ARMONIZADO' in final_fondo_sel or 'ACCION EUROSTOXX 50 ETF, FI COTIZADO ARMONIZADO' in final_fondo_sel:
            st.text('AVISO: ACCION IBEX 35 ETF, FI COTIZADO ARMONIZADO y ACCION EUROSTOXX 50 ETF, FI COTIZADO ARMONIZADO reportan remuneración de la liquidez, en lugar de rentabilidad media de la liquidez.'
                'Para la comparación entre fondos, se asumen similares.')
        if len(info_filtered)>0:
          st.table(info_filtered[['fondo','name','registro_CNMV','nif','email_gest','rating_depos','riesgo']].set_index('fondo'))
    with graphs:    #hacer gráficos!!!!
      if len(data_clean) > 0:
        for var in input_vars:
          c= alt.Chart(data_filtered[['fondo','period',var]]).mark_line(point=True).encode(x='period', y=var, color='fondo', tooltip=['fondo','period',var])
          st.altair_chart(c, use_container_width=True)

          #['fondo', 'name', 'ISIN', 'registro_CNMV', 'gestora', 'email_gest', 'depos', 'rating_depos', 'riesgo']