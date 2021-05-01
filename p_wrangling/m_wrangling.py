import pandas as pd
import os
import streamlit as st
from tqdm import tqdm

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def create_df(path='data/csv',limit=False,created=False):
    df=False
    i=0
    for file in tqdm(os.listdir('data/csv')):
        if type(df) == bool:
            df = pd.read_csv(f'data/csv/{file}', sep='*')
            if created:
                try:df = df.append(pd.read_csv(f'data/created_data/{file}', sep='*'))
                except:pass
        else:
            df = df.append(pd.read_csv(f'data/csv/{file}', sep='*'))
            if created:
                try:df = df.append(pd.read_csv(f'data/created_data/{file}', sep='*'))
                except:pass
        #print(file, 'parsed')
        i += 1
        if limit and i>20:
            return df
    return df.reset_index(drop=True)


def load_fondo(fondo,path='data/csv',created=False):
    df=pd.read_csv(f'{path}/{fondo}.csv', sep='*')
    if created:
        try:df = df.append(pd.read_csv(f'data/created_data/{fondo}.csv', sep='*'))
        except:pass
    #print(fondo, 'parsed')
    return df


def load_gen_data(fondo,path='data/csv_gen_info'):
    df=pd.read_csv(f'{path}/{fondo}.csv', sep='*')
    df['fondo']=fondo
    if 'link' in df.columns:
        df.drop('link',axis=1,inplace=True)
    #print(fondo, 'parsed')
    return df


def wrang_main(df):

    #converting vars
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])

    #filling nulls
    df['riesgo'].fillna('ND', inplace=True)
    df['rentab_avg'].fillna(df['remun_liq'], inplace=True)

    #cleaning data
    df['dividendos']=df['dividendos'].apply(div_clean)
    for i in ['beneficio','rentab_IIC_trim', 'volat_vl_trim', 'ratio_gastos_trim',
              'comision_gest_pat','comision_gest_res','comision_gest_total',
              'comision_depos']:
        df[i] = df[i].apply(parse_strings)

    df['period_type'] = df.apply(lambda x: period_type(x['period']), axis=1)
    df['year'] = df.apply(lambda x: x['start_date'].year, axis=1)

    return df

def inspect_data(fondo):
     fondo_df=pd.read_csv(f'data/csv/{fondo}.csv', sep='*')
     return fondo_df

def yearly_data(S1,S2):
    array=[]
    mean_vars=['rotacion','rentab_avg','remun_liq','n_participaciones',
               'n_participes', ]
    sum_vars=['beneficio','comision_gest_pat','comision_gest_res','comision_gest_total',
              'comision_depos']
    copy_vars=['fondo','name', 'end_date','registro_CNMV', 'patrimonio', 'valor_liq','riesgo','clase']

    null_vars= ['rentab_IIC_trim',
               'volat_vl_trim','ratio_gastos_trim']

    calc_vars=['period', 'start_date','dividendos','period_type', 'year']

    columns=['fondo', 'name', 'period', 'start_date', 'end_date', 'riesgo',
       'rotacion', 'rentab_avg', 'remun_liq', 'n_participaciones',
       'n_participes', 'beneficio', 'patrimonio', 'dividendos', 'valor_liq',
       'comision_gest_pat', 'comision_gest_res', 'comision_gest_total',
       'comision_depos', 'rentab_IIC_trim', 'volat_vl_trim',
       'ratio_gastos_trim', 'clase', 'period_type', 'year']

    for i in range(len(columns)):
        variable=columns[i]
        if variable in mean_vars:
            array.append((S1[i]+S2[i])/2)
        elif variable in sum_vars:
            array.append(S1[i]+S2[i])
        elif variable in copy_vars:
            array.append(S2[i])
        elif variable in calc_vars:
            if variable=='period':
                array.append(f'{S1[i][:4]}')
            elif variable=='start_date':
                array.append(S1[i])
            elif variable == 'dividendos':
                try:array.append(bool(S1[i]+S2[i]))
                except: array.append(False)
            elif variable=='period_type':
                array.append('Y')
            elif variable=='year':
                array.append(S1.period[:4])
        elif variable in null_vars:
            array.append(None)
    return array

def period_type(x):
    if 'S' in x:
        return 'S'
    elif 'T' in x:
        return 'T'
    else:
        return 'Y'

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

def create_data(df,merge=True, save=False):
    df.reset_index(drop=True, inplace=True)
    df_calc = False
    for fondo in tqdm(df.fondo.unique()):
        #print(fondo)
        df_fondo=df[df.fondo==fondo]
        for year in df_fondo.year.unique():
            #print(year)
            df_year=df_fondo[(df_fondo.year==year)]
            names = df_year.name.unique()
            for name in names:
                if df_year.clase.sum() > 0:
                    df_name=df_year[df_year.name==name]
                else: df_name=df_year
                tempY=''
                tempT2=''
                tempT4=''
                try:S1=df_name.loc[df_name.period==f'{year} S1'].squeeze(axis=0)
                except:S1 = ''
                try: S2 = df_name.loc[df_name.period == f'{year} S2'].squeeze(axis=0)
                except: S2 = ''
                try:T1=df_name.loc[df_name.period==f'{year} T1'].squeeze(axis=0)
                except:T1 = ''
                try:T3=df_name.loc[df_name.period==f'{year} T3'].squeeze(axis=0)
                except:T3 = ''
                #print(type(S1),type(S2),type(T1),type(T3))
                #print(len(S1),len(S2),len(T1),len(T3))
                if len(S1)>0 and len(S2)>0:
                    tempY=yearly_data(S1, S2)
                if len(S1)>0 and len(T1)>0:
                    tempT2=T2_data(T1,S1)
                if len(T3)>0 and len(S2)>0:
                    tempT4=T4_data(T3,S2)

                temp_list=[tempY,tempT2,tempT4]
                #print(temp_list)
                for datum in temp_list:
                    if datum!='':
                        if type(df_calc)==bool:
                            col_list = ['fondo', 'name', 'period', 'start_date', 'end_date', 'riesgo',
                                        'rotacion', 'rentab_avg', 'remun_liq', 'n_participaciones',
                                        'n_participes', 'beneficio', 'patrimonio', 'dividendos', 'valor_liq',
                                        'comision_gest_pat', 'comision_gest_res', 'comision_gest_total',
                                        'comision_depos', 'rentab_IIC_trim', 'volat_vl_trim',
                                        'ratio_gastos_trim', 'clase', 'period_type', 'year']
                            df_calc = pd.DataFrame(datum,index=col_list).T
                        else:
                            df_calc.loc[len(df_calc)] = datum

    df_calc=wrang_main(df_calc)
    if save:
        for fondo in df_calc.fondo.unique():
            clean_fondo = fondo.replace('/', '-')
            df_calc[df_calc.fondo==fondo].to_csv(f'data/created_data/{clean_fondo}.csv', sep='*', index=False)

    if merge and type(df_calc)!=bool:
        df_calc=pd.concat([df,df_calc])
        return df_calc
    elif merge==False:
        return df_calc   #devuelve un False, si no hay dataframe
    else:
        return df

def T2_data(T1,S1):
    array=[]
    mean_vars=['rotacion','rentab_avg','remun_liq','n_participaciones',
               'n_participes', ]
    sum_vars=['beneficio','comision_gest_pat','comision_gest_res','comision_gest_total',
              'comision_depos']
    copy_vars=['fondo','name', 'end_date','registro_CNMV', 'patrimonio', 'valor_liq','riesgo','clase']

    null_vars= ['rentab_IIC_trim',
               'volat_vl_trim','ratio_gastos_trim']

    calc_vars=['period', 'start_date','dividendos','period_type', 'year']

    columns=['fondo', 'name', 'period', 'start_date', 'end_date', 'riesgo',
       'rotacion', 'rentab_avg', 'remun_liq', 'n_participaciones',
       'n_participes', 'beneficio', 'patrimonio', 'dividendos', 'valor_liq',
       'comision_gest_pat', 'comision_gest_res', 'comision_gest_total',
       'comision_depos', 'rentab_IIC_trim', 'volat_vl_trim',
       'ratio_gastos_trim', 'clase', 'period_type', 'year']

    for i in range(len(columns)):
        variable=columns[i]
        if variable in mean_vars:
            array.append((2*S1[i]-T1[i]))
        elif variable in sum_vars:
            array.append(S1[i]-T1[i])
        elif variable in copy_vars:
            array.append(S1[i])
        elif variable in calc_vars:
            if variable=='period':
                array.append(f'{S1[i][:4]} T2')
            elif variable=='start_date':
                array.append(T1[i])
            elif variable == 'dividendos':
                try: array.append(bool(T1[i]+S1[i]))
                except:array.append(False)
            elif variable=='period_type':
                array.append('Y')
            elif variable=='year':
                array.append(S1[2][:4])
        elif variable in null_vars:
            array.append(None)

    return array

def T4_data(T3,S2):
    array=[]
    mean_vars=['rotacion','rentab_avg','remun_liq','n_participaciones',
               'n_participes', ]
    sum_vars=['beneficio','comision_gest_pat','comision_gest_res','comision_gest_total',
              'comision_depos']
    copy_vars=['fondo','name', 'end_date','registro_CNMV', 'patrimonio', 'valor_liq','riesgo','clase']

    null_vars= ['rentab_IIC_trim',
               'volat_vl_trim','ratio_gastos_trim']

    calc_vars=['period', 'start_date','dividendos','period_type', 'year']

    columns=['fondo', 'name', 'period', 'start_date', 'end_date', 'riesgo',
       'rotacion', 'rentab_avg', 'remun_liq', 'n_participaciones',
       'n_participes', 'beneficio', 'patrimonio', 'dividendos', 'valor_liq',
       'comision_gest_pat', 'comision_gest_res', 'comision_gest_total',
       'comision_depos', 'rentab_IIC_trim', 'volat_vl_trim',
       'ratio_gastos_trim', 'clase', 'period_type', 'year']

    for i in range(len(columns)):
        variable=columns[i]
        if variable in mean_vars:
            array.append((2*S2[i]-T3[i]))
        elif variable in sum_vars:
            array.append(S2[i]-T3[i])
        elif variable in copy_vars:
            array.append(S2[i])
        elif variable in calc_vars:
            if variable=='period':
                array.append(f'{S2[i][:4]} T4')
            elif variable=='start_date':
                array.append(T3[i])
            elif variable == 'dividendos':
                try:array.append(bool(T3[i]+S2[i]))
                except:array.append(False)
            elif variable=='period_type':
                array.append('Y')
            elif variable=='year':
                array.append(S2[2][:4])
        elif variable in null_vars:
            array.append(None)

    return array