import argparse
import os
import requests
from bs4 import BeautifulSoup
import datetime
from tqdm import tqdm
import pandas as pd
import numpy as np
import streamlit
import p_acquisition.m_acquisition as acq
import p_wrangling.m_wrangling as wra
import p_analysis
import p_reporting

fondos=['AMUNDI CORTO PLAZO, FI', 'CAIXABANK BOLSA ALL CAPS ESPAÑA, FI',
       'CAIXABANK BOLSA GESTION EURO, FI',
       'CAIXABANK COMUNICACION MUNDIAL, FI',
       'CAIXABANK DIVERSIFICADO DINAMICO, FI',
       'CAIXABANK OPORTUNIDAD, FI',
       'CAIXABANK RENTA FIJA ALTA CALIDAD CREDITICIA, FI',
       'CAIXABANK RENTA FIJA DOLAR, FI',
       'CAIXABANK RF DURACION NEGATIVA, FI',
       'CAIXABANK SELECCION ALTERNATIVA, FI', 'CALIOPE, FI',
       'FIDEFONDO, FI', 'FONDITEL ALBATROS, FI',
       'FONDITEL BOLSA MUNDIAL SOSTENIBLE, FI',
       'FONDITEL RENTA FIJA MIXTA INTERNACIONAL, FI',
       'INVERSABADELL 10, FI', 'INVERSABADELL 25, FI',
       'INVERSABADELL 50, FI', 'INVERSABADELL 70, FI',
       'SABADELL AMERICA LATINA BOLSA, FI',
       'SABADELL ASIA EMERGENTE BOLSA, FI',
       'SABADELL BONOS ALTO INTERES, FI', 'SABADELL BONOS EMERGENTES, FI',
       'SABADELL BONOS ESPAÑA, FI', 'SABADELL BONOS EURO, FI',
       'SABADELL BONOS FLOTANTES EURO, F.I.',
       'SABADELL BONOS INFLACIÓN EURO F.I.',
       'SABADELL BONOS INTERNACIONAL, FI', 'SABADELL DINAMICO, FI',
       'SABADELL DOLAR FIJO, FI', 'SABADELL EMERGENTE MIXTO FLEXIBLE, FI',
       'SABADELL EQUILIBRADO, FI', 'SABADELL ESPAÑA BOLSA, FI',
       'SABADELL ESPAÑA DIVIDENDO, FI',
       'SABADELL ESTADOS UNIDOS BOLSA, FI', 'SABADELL EURO YIELD, FI',
       'SABADELL EUROACCION, FI', 'SABADELL EUROPA BOLSA, FI',
       'SABADELL EUROPA EMERGENTE BOLSA, FI', 'SABADELL EUROPA VALOR, FI',
       'SABADELL FINANCIAL CAPITAL, FI', 'SABADELL INTERES EURO, FI',
       'SABADELL INVERSION ETICA Y SOLIDARIA, FI',
       'SABADELL JAPON BOLSA, FI', 'SABADELL PRUDENTE, FI',
       'SABADELL RENDIMIENTO, FI', 'SABADELL SELECCIÓN ALTERNATIVA, FI']
dict_links=acq.get_links_from_csv()
i=0
for fondo in fondos:
    a=datetime.datetime.now()
    print(f'{i}/{len(fondos)} - {fondo}-{a}')
    if os.path.isfile(f'data/csv/{fondo}.csv'):
        os.remove(f'data/csv/{fondo}.csv')
    #   print(f'{fondo}.csv deleted')
    link=dict_links[fondo]
    try:acq.get_info_fondo(fondo,link)
    except:
        import json
        import telegram
        def notify_ending(message):
            with open('../keys.json', 'r') as keys_file:
                k = json.load(keys_file)
                token = k['telegram_token']
                chat_id = k['telegram_chat_id']
            bot = telegram.Bot(token=token)
            bot.sendMessage(chat_id=chat_id, text=message)

        notify_ending('ha petau')
        raise EOFError
    i+=1

    print(f'Elapsed time: {(datetime.datetime.now() -a).total_seconds()/60} minutes')

fondo_df=wra.inspect_data(fondo)
print('finished!')

