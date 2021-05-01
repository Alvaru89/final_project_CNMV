import argparse
import os
import requests
from bs4 import BeautifulSoup
import datetime
from tqdm import tqdm
import pandas as pd
import numpy as np
import streamlit
import p_acquisition.m_acquisition_lean as acq
import p_wrangling.m_wrangling as wra
import p_analysis
import p_reporting

fondos=[]
dict_links=acq.get_links_from_csv()
i=0
for fondo in fondos:
    a=datetime.datetime.now()
    print(f'{i}/{len(fondos)} - {fondo}-{a}')
    #if os.path.isfile(f'data/csv/{fondo}.csv'):
    #    os.remove(f'data/csv/{fondo}.csv')
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

