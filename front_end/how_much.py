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
        data=load_fondo(fondo_selected ,path)
        data_clean = wrang_main(data)
        data_clean=data_clean[['name','period','rentab_avg','comision_gest_pat',
                              'comision_gest_res','comision_gest_total','comision_depos','year','period_type']]



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
        data_filtered.reset_index(drop=True,inplace=True)
        inversion=calculator(float(input_qty), data_filtered)
        data_filtered['inversion']=inversion


    with display_col:
      info = st.beta_container()
      graphs = st.beta_container()

      with info:

          if len(data_filtered) > 0 and periodo_sel!='':
              data_filtered = data_filtered.groupby('period').mean()
              st.write(f'Si hubieras invertido {input_qty}€ en {fondo_selected} en {periodo_sel}, ahora tendrías {list(data_filtered.inversion)[-1]}')
              st.dataframe(data_filtered[['inversion','rentab_avg','comision_gest_pat','comision_gest_res','comision_gest_total','comision_depos']])

      with graphs:  # hacer gráficos!!!!
        if len(data_filtered) > 0:
            st.bar_chart(data_filtered['inversion'])
            st.line_chart(data_filtered['rentab_avg'])
            comisiones=['comision_gest_pat','comision_gest_res','comision_gest_total','comision_depos']
            st.line_chart(data_filtered[comisiones])


def calculator (cantidad,df):
    arr=[cantidad]
    for i in range(1,len(df)):
        qty=arr[i-1]
        delta=qty*df.rentab_avg[i]/100

        if str(df.comision_gest_pat[i])!='nan':
            com_pat = -qty*df.comision_gest_pat[i]/100
        else:
            com_pat=0
        if str(df.comision_gest_res[i])!='nan' and delta>0:
            com_res = -delta*df.comision_gest_res[i]/100
        else:
            com_res=0

        if str(df.comision_depos[i])!='nan':
            com_depos = -(qty + delta) * df.comision_depos[i]/100
        else:com_depos=0

        com_total = -(qty + delta) * df.comision_gest_total[i]/100
        if com_total < com_pat + com_res: arr.append(qty+delta+com_total+com_depos)
        else:arr.append(qty+delta+com_pat+com_res+com_depos)
    return arr