import datetime
import streamlit as st

selection_col, display_col = st.beta_columns(2)
with selection_col:
  st.header('Comparador de fondos')
  # st.text('Cargando base de datos)

  # data=pd.DataFrame.
  fondos_selected=[]
  selection_col, display_col = st.beta_columns(2)
  #buscador de fondos
  input_text = st.text_input('Escribe aqui el fondo')
  if st.button("apply") and input_text:
    output = [_  for _ in data.fondo.unique() if input_text is in _]
    input_fondo=st.selectbox(output)
  fondos_selected=fondos_selected.append(input_fondo)

  if st.button("Borrar selección de fondos"):
    fondos_selected=[]

  year_start=data.year.min() #ver minimo
  year_end=datetime.date.year
  input_years = st.slider("Label", year_start, year_end, (x1, x2), 1)
  input_period = selection_col.selectbox('¿Periodo?', options=['Trimester','Semester','Year'], index=0)
  input_vars = st.multiselect('¿Qué variables te gustaría comparar? (Máximo recomendado 3)', NUM VARS) # especificar variables numericas

  mask_fondo=data['fondo'].isin(fondos_selected)
  mask_vars= data[input_variable]
  mask_years=data['year']
  mask_period=data[period_type]==input_period
  data_filtered = data[mask_fondo&mask_vars&mask_years&mask_period]

with display_col:
  #hacer gráficos!!!!
    graphs=st.beta_container(len(input_var)) #no se si funciona probar bucle if si no funciona
    for graph in graphs:
      st.bar_chart(np.random.randn(50, 3))
