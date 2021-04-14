import argparse
import os
import requests
from bs4 import BeautifulSoup
import datetime
import tqdm
import pandas as pd
import numpy as np
import streamlit
import p_acquisition.m_acquisition as acq
import p_wrangling.m_wrangling as wra
import p_analysis
import p_reporting


fondo='AVANCE GLOBAL, FI'
if os.path.isfile(f'data/csv/{fondo}.csv'):
    os.remove(f'data/csv/{fondo}.csv')
    print(f'{fondo}.csv deleted')

dict_links=acq.get_links_from_csv()
link=dict_links[fondo]

acq.get_info_fondo(fondo,link)
# print(f'{fondo}.csv created')

fondo_df=wra.inspect_data(fondo)
print('finished!')

