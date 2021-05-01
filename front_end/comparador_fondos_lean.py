import datetime
import streamlit as st
from p_wrangling.m_wrangling import wrang_main,load_fondo,load_gen_data,create_data
import altair as alt
import os
import pandas as pd

def comp_fondos_web():
  selection_col, display_col = st.beta_columns([1, 3])
  final_fondo_sel=[]
  with selection_col:
    # st.header('Comparador de fondos')
    # st.text('Cargando base de datos')

    path = 'data/csv'
    path2='data/csv_gen_info'
    fondo_list=[file.split('.csv')[0] for file in os.listdir(path)]
    fondo_list.sort()
    #buscador de fondos
    #input_text = st.text_input('Escribe aqui el fondo')

    # if input_text:
    #   storage = final_fondo_sel
    #   output = [x for x in fondo_list if input_text.lower() in x.lower()]
    #   fondos_selected = st.multiselect("Elige fondos a comparar", output)
    #   final_fondo_sel +=fondos_selected
    # else:
    fondos_selected = st.multiselect("Elige fondos a comparar", fondo_list)
    final_fondo_sel +=fondos_selected
    storage = final_fondo_sel

    data=''
    data_clean=''
    gen_data = ''
    for fondo in final_fondo_sel:
        if len(data)==0:
            data=load_fondo(fondo,path)
            data_clean = create_data(wrang_main(data))
            gen_data=load_gen_data(fondo,path2)
        else:
          data=pd.concat([data,load_fondo(fondo,path)])
          data_clean = create_data(wrang_main(data))
          gen_data = pd.concat([gen_data, load_gen_data(fondo, path2)])

    if len(data_clean)>0:
      year_start=int(data_clean.year.min())-1 #ver minimo del dataframe, el -1 es para evitar problemas en fondos de 2020
    else: year_start=2000
    if len(data_clean)>0:
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
      mask_period=data_clean['period_type']==input_period[0]
      data_filtered = data_clean[mask_years & mask_period]
      data_filtered.sort_values('end_date', ascending=True, inplace=True)

  with display_col:
    info_expander = st.beta_expander(f"Info general de los fondos")
    graphs = st.beta_container()

    with info_expander:   #ultima info disponible fondo
        # st.text(f'Fondos seleccionados: {final_fondo_sel}')
        if len(gen_data)>0:
            st.table(gen_data.set_index('fondo').T)
    with graphs:    #hacer gráficos!!!!
      if len(data_clean) > 0:
        for var in input_vars:
            if data_filtered.clase.sum()>0:
                fondo_clase='name'
            else:
                fondo_clase = 'fondo'
            c= alt.Chart(data_filtered[['fondo','name','period',var]]).mark_line(point=True).encode(x='period', y=var, color=fondo_clase, tooltip=['fondo','name','period',var])
            st.altair_chart(c, use_container_width=True)