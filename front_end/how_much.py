import datetime
import streamlit as st
from p_wrangling.m_wrangling import wrang_main,load_fondo
import altair as alt
import os
import pandas as pd

def how_much():
  selection_col, display_col = st.beta_columns([1, 3])

  with selection_col:

    path = 'data/csv'
    path2='data/csv_gen_info'
    fondo_list=[file.split('.csv')[0] for file in os.listdir(path)]
    fondo_list.sort()
    #buscador de fondos
    input_text = st.text_input('Escribe aqui el fondo')

    if input_text:
      output = [x for x in fondo_list if input_text.lower() in x.lower()]
      fondo_selected = st.selectbox("Elige el fondo de inversión", output)
    else:
      fondo_selected = st.selectbox("Elige el fondo de inversión", fondo_list)

    input_qty = st.text_input('Escribe aqui la cantidad(€)')

    data=''
    data_clean=''
    data_filtered = ''
    periodo_sel=''
    if len(data)==0 and fondo_selected:
        clean_fondo = fondo_selected.replace('/', '-')
        data=load_fondo(fondo_selected ,path, created=True)
        data_created=pd.read_csv(f'data/created_data/{clean_fondo}.csv', sep='*')
        data_clean = pd.concat([wrang_main(data), wrang_main(data_created)])

    else:
        mask3=[True for x in range(len(data_clean))]
    if len(data_clean)>0:
      year_start=int(data_clean.year.min())
    else: year_start=2000
    if len(data_clean)>0:
      year_end = int(data_clean.year.max())  # ver minimo del dataframe
    else: year_end=datetime.date.today().year
    year_inv = st.slider("Año de comienzo de la inversión", year_start, year_end, year_start, 1)



    periodo_inv = st.selectbox("Trimestre de comienzo de la inversión", options= ['T1','T2','T3','T4'], index=0)
    periodo_sel=f'{year_inv} {periodo_inv}'

    if st.button('Calcular'):
      if len(data) > 0 and periodo_sel!='':
        mask1=data_clean.period_type=='T'
        mask2=data_clean.period>=periodo_sel
        data_filtered=data_clean[mask1&mask2]
        if data_filtered.clase.sum() > 0:
            data_filtered.groupby('period').mean()
        data_filtered.drop_duplicates('period', inplace=True)
        data_filtered.sort_values(['name','period'],ascending=True,inplace=True)
        data_filtered.reset_index(drop=True,inplace=True)
        inversion_vl=calculator_vl(float(input_qty), data_filtered)
        data_filtered['inversion']=inversion_vl

    with display_col:
      info = st.beta_container()
      graphs = st.beta_container()

      with info:
          # with st.beta_expander('Disclaimer'):
          #     st.write('Estos valores son solo una aproximación calculada en base a la fórmula simplificada:')
          #     st.write('Valor de la inversión = Valor previo + Ganancias (rentabilidad y beneficios) - Comisiones (gestora y depositaria)')

          if len(data_filtered) > 0 and periodo_sel!='':
              data_filtered = data_filtered.groupby('period').mean()
              st.markdown(f'Si hubieras invertido **{input_qty}€** en **{fondo_selected}** en **{periodo_sel}**, ahora tendrías aproximadamente **{int(list(data_filtered.inversion)[-1])}€**.')
              st.dataframe(data_filtered[['inversion','valor_liq','rentab_avg','beneficio','comision_gest_pat','comision_gest_res','comision_gest_total','comision_depos']])

      with graphs:  # hacer gráficos!!!!
        if len(data_filtered) > 0:
            st.area_chart(data_filtered[['inversion']])
            st.line_chart(data_filtered['valor_liq'])
            st.line_chart(data_filtered['rentab_avg'])
            comisiones=['comision_gest_pat','comision_gest_res','comision_gest_total','comision_depos']
            st.line_chart(data_filtered[comisiones])

def calculator_vl (cantidad,df):
    arr=[cantidad]
    part=cantidad/df.valor_liq[0]
    for i in range(1,len(df)):
        vl_new=df.valor_liq[i]
        new_qty=part*vl_new
        arr.append(new_qty)
    return arr