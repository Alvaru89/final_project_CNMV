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


def inspect_data(fondo):
     fondo_df=pd.read_csv(f'data/csv/{fondo}', sep='*')
     return fondo_df