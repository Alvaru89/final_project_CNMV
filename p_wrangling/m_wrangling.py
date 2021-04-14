import pandas as pd
import numpy as np

def create_df():
    df=False
    for file in os.listdir('data/csv'):
        print(file, 'parsed')
        if type(df)==bool:
            df=pd.read_csv(f'data/csv/{file}', sep='*')
        else:
            df=df.append(pd.read_csv(f'data/csv/{file}', sep='*'))
    return df

def nulls_treat():
    return

def wrang_main(df):
    # drop_duplicates

    #converting vars
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    #new cols
    df['period_type'] = df.apply(lambda x: period_type(x['period']), axis=1)
    df['year'] = df.apply(lambda x: x['start_date'].year, axis=1)

    return df

def inspect_data(fondo):
     fondo_df=pd.read_csv(f'data/csv/{fondo}.csv', sep='*')
     return fondo_df


def period_type(x):
    if 'Semester' in x:
        return 'Semester'
    elif 'Trimester' in x:
        return 'Trimester'