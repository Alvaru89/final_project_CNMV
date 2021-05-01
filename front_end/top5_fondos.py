import streamlit as st
from p_wrangling.m_wrangling import wrang_main,create_df,load_gen_data
import pandas as pd

def top5():
    selection_col, display_col = st.beta_columns([1, 5])
    result=''
    with selection_col:
        data=create_df(created=True)
        data_clean=wrang_main(data)

        year_start=int(data_clean.year.min())
        year_end = int(data_clean.year.max())-1
        year_input = st.selectbox("Año", options= [x for x in range(year_start,year_end+1)][::-1], index=0)

        periodo_input = st.selectbox("Trimestre", options= ['T1','T2','T3','T4','S1','S2', 'Y'], index=0)
        if periodo_input!='Y':
            period_full=f'{year_input} {periodo_input}'
        else:
            period_full = f'{year_input}'
        data_filtered=data_clean[data_clean.period == period_full]

    with display_col:
        st.write(f'Los mejores fondos en {period_full} son:')
        result=data_filtered.sort_values('rentab_avg', ascending=False,).reset_index(drop=True).loc[:5,:][['fondo', 'name', 'rentab_avg', 'rotacion','rentab_IIC_trim', 'volat_vl_trim', 'ratio_gastos_trim']]
        st.dataframe(result.set_index('fondo'))
        if len(result)!=0:
            gen_data = ''
            for fondo in result.fondo:
                if len(gen_data) == 0:
                    gen_data = load_gen_data(fondo)
                else:
                    gen_data = pd.concat([gen_data, load_gen_data(fondo)])
            info_expander = st.beta_expander("Info general de los fondos del top5")
            with info_expander:
                if len(gen_data) > 0:
                    st.table(gen_data.set_index('fondo').T)



