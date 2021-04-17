import datetime
import streamlit as st
from p_wrangling.m_wrangling import create_df,wrang_main
import altair as alt

def comp_fondos_web():
  selection_col, display_col = st.beta_columns([1, 3])

  with selection_col:
    st.header('Comparador de fondos')
    # st.text('Cargando base de datos')
    data = create_df(path='data/csv',limit=True)   #pendiente a la version limpia
    data=wrang_main(data)

    fondos_selected=[]
    input_fondo=''
    fondo_list=data.fondo.unique()
    #buscador de fondos
    input_text = st.text_input('Escribe aqui el fondo')

    if st.button("Search") and input_text:
      output = [x for x in fondo_list if input_text.lower() in x.lower()]
      input_fondo=st.selectbox('Selecciona el fondo',output)
    if input_fondo!='':
      fondos_selected=fondos_selected.append(input_fondo)
    st.text(f'Fondos seleccionados: {fondos_selected}')

    if st.button("Borrar selección de fondos"):
      fondos_selected=[]

    year_start=int(data.year.min()) #ver minimo
    year_end=int(datetime.date.today().year)
    input_years = st.slider("Label", year_start, year_end, (year_start, year_end), 1)
    x1,x2=input_years
    input_period = selection_col.selectbox('¿Periodo?', options=['Trimester','Semester','Year'], index=0)

    vars_list=['rotacion', 'rentab_avg',
              'n_participaciones', 'n_participes',
              'beneficio', 'patrimonio',
               'valor_liq',
              'comision_gest_total', #'comision_depos',
              'rentab_IIC_trim',
              'volat_vl_trim', 'ratio_gastos_trim']
    input_vars = st.multiselect('¿Qué variables te gustaría comparar? (Máximo recomendado 3)', vars_list) # especificar variables numericas

    mask_fondo=data['fondo'].isin(fondos_selected)
    mask_years=data['year']
    mask_period=data['period_type']==input_period
    data_filtered = data[mask_fondo&mask_years&mask_period]

  with display_col:
    #hacer gráficos!!!!
      graphs=st.beta_container() #no se si funciona probar bucle if si no funciona
      for var in input_vars:
        viz_data=data[['fondo','period',var]]
        c= alt.Chart(viz_data).mark_line(point=True).encode(x='period', y=var, color='fondo', tooltip=['fondo','period',var])
        st.altair_chart(c, use_container_width=True)
