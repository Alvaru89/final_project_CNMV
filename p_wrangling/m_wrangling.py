import pandas as pd
import numpy as np
import os
import streamlit as st

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def create_df(path='data/csv',limit=False):
    df=False
    i=0
    for file in os.listdir('data/csv'):
        if type(df)==bool:
            df=pd.read_csv(f'data/csv/{file}', sep='*')
        else:
            df=df.append(pd.read_csv(f'data/csv/{file}', sep='*'))
        print(file, 'parsed')
        i += 1
        if limit and i>20:
            return df
    return df

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def load_fondo(fondo,path='data/csv'):
    df=pd.read_csv(f'{path}/{fondo}.csv', sep='*')
    #print(fondo, 'parsed')
    return df

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def load_gen_data(fondo,path='data/csv_gen_info'):
    df=pd.read_csv(f'{path}/{fondo}.csv', sep='*')
    df['fondo']=fondo
    df.drop('link',axis=1,inplace=True)
    #print(fondo, 'parsed')
    return df

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def wrang_main(df):
    # drop_duplicates

    #converting vars
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    #new cols
    df['period_type'] = df.apply(lambda x: period_type(x['period']), axis=1)
    df['year'] = df.apply(lambda x: x['start_date'].year, axis=1)
    #filling nulls
    #df['rating_depos'].fillna('ND',inplace=True)
    df['riesgo'].fillna('ND', inplace=True)
    df['rentab_avg'].fillna(df['remun_liq'], inplace=True)

    #cleaning data
    df['dividendos']=df['dividendos'].apply(div_clean)
    for i in ['rentab_IIC_trim', 'volat_vl_trim', 'ratio_gastos_trim']:
        df[i] = df[i].apply(parse_strings)
    return df

def inspect_data(fondo):
     fondo_df=pd.read_csv(f'data/csv/{fondo}.csv', sep='*')
     return fondo_df

def yearly_data():
    mean_vars=['rotacion','rentab_avg','remun_liq','n_participaciones',
               'n_participes', 'patrimonio','valor_liq','rentab_IIC_trim',
               'volat_vl_trim','ratio_gastos_trim',]
    sum_vars=['beneficio','comision_gest_pat','comision_gest_res','comision_gest_total',
              'comision_depos','dividendos']
    copy_vars=['fondo','name','nif','registro_CNMV', 'email_gest', 'rating_depos', 'riesgo',
               'gestora','depos','ISIN']
    period=f'{year} Y'
    start_date=f'{year}-01-01'
    end_date = f'{year}-12-31'
    #vigilar dividendos que es booleana
    return

def period_type(x):
    if 'S' in x:
        return 'S'
    elif 'T' in x:
        return 'T'

def div_clean(x):
    if type(x)==str:
        if x.strip().lower()=='false' or x.strip().lower()=='[]':
            return False
        if x.strip().lower()== 'true':
            return True
    if type(x)==bool:
        return x

def parse_strings(x):
    try: return float(x)
    except: return None

# def make_clickable(link):
#     return f'<a target="_blank" href="{link}">Link</a>'