import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import numpy as np
import os

def get_links_from_web():
    no_pages = 124  # automatizar?
    dict_links = {}
    for page in range(no_pages):
        url = f'https://www.cnmv.es/portal/Consultas/MostrarListados.aspx?id=3&page={str(page)}'
        sopa_listado = BeautifulSoup(requests.get(url).content, 'html.parser')
        results = sopa_listado.find_all('li', {'id': "elementoPrimerNivel"})

        for result in results:
            short_link = result.find('a')['href']
            link = 'https://www.cnmv.es/portal/Consultas/' + str(short_link)
            descr = result.find('a')['title']
            dict_links[descr] = link

    a = pd.DataFrame.from_dict(dict_links, orient='index', columns=['links'])
    a.to_csv('data/dict_links.csv')
    print("links saved in data/dict_links.csv")
    return dict_links

def get_links_from_csv():
    a = pd.read_csv('data/dict_links.csv', index_col=0)
    dict_links = a.to_dict(orient='dict')
    dict_links = dict_links['links']
    return dict_links

def get_info_fondo(fondo,link):
    nif = link[-9:-1]
    clean_fondo=fondo.replace('/','-')
    if os.path.isfile(f'data/csv/{clean_fondo}.csv'):
        # print(fondo, 'skipped!')
        return
    print(f'extracting {fondo}')
    web_fondo=requests.get(link+'&vista=0')
    sopa_fondo = BeautifulSoup(web_fondo.content, 'html.parser')
    gestora=sopa_fondo.find('table',{'id':"ctl00_ContentPrincipal_gridGestora"}).find('a').text
    depos=sopa_fondo.find('table',{'id':"ctl00_ContentPrincipal_gridDepositaria"}).find('a').text
    fecha_reg = sopa_fondo.find('td', {'data-th': "Fecha registro oficial"}).text
    fecha_reg = datetime.datetime.strptime(fecha_reg, '%d/%m/%Y')
    fecha_fin = sopa_fondo.find('td', {'data-th': "Fecha último folleto"}).text
    fecha_fin = datetime.datetime.strptime(fecha_fin, '%d/%m/%Y')
    start = fecha_reg.year
    end = fecha_fin.year + 1
    try:
        ISIN = sopa_fondo.find('td', {'data-th': "ISIN"}).find('a').text
    except:
        ISIN = ''

    temp = False
    for year in range(start, end):
        url_year = link + f'&vista=1&fs=01%2f02%2f{year}'
        # print(url_year)
        web_fondo_year = requests.get(url_year)  # con requests
        sopa_fondo = BeautifulSoup(web_fondo_year.content, 'html.parser')

        tables = sopa_fondo.find('div', {'id': "ctl00_ContentPrincipal_pnIPPS"})
        if tables == None:
            continue
        tds = tables.find_all('td', {'data-th': "Documentos"})
        for td in tds:
            pdf_link = 'https://www.cnmv.es/portal/Consultas/' + str(td.find_all('a')[0]['href'][3:])
            #             print(pdf_link)
            xbrl_link = 'https://www.cnmv.es/portal/Consultas/' + str(td.find_all('a')[1]['href'][3:])
            #             print(xbrl_link)

            xbrl = requests.get(xbrl_link)
            fondo_info=xml_scrap_main(xbrl.content, nif, fondo)

            for n in range(len(fondo_info)):
                fondo_info[n].update({'gestora': gestora, 'depos': depos, 'ISIN': ISIN})

            if type(temp) == bool:
                temp = pd.DataFrame.from_dict(fondo_info[0], orient='index', columns=['0']).T
            else:
                for i in range(0, len(fondo_info)):
                    temp = temp.append(other=fondo_info[i], ignore_index=True)

    if type(temp)!= bool:  #exportado
        temp.to_csv(f'data/csv/{clean_fondo}.csv', sep='*', index=False)
        print(f'{clean_fondo}.csv created!')
    else:
        print(f'ALERT {fondo} has no data!!!')
    return


def xml_scrap_main(xbrl, nif, fondo):
    xml_soup = BeautifulSoup(xbrl, 'lxml')
    #     print('xml_soup created with xml_scrap')
    #     print(xml_soup)

    clases = xml_soup.find_all('iic-com:denominacionclase')
    if clases != []:
        fondo_dict_list = []
        for i in range(len(clases)):
            fondo_dict_list.append(xml_scrap_clase(xml_soup, nif, fondo, i))
        return fondo_dict_list
    else:
        return [xml_scrap(xml_soup, nif, fondo)]


def xml_scrap(xml_soup, nif, fondo):
    name = xml_soup.find(['xbrli:identifier','identifier']).text
    #     periodo
    startdate = str(xml_soup.find(['xbrli:startdate','startdate']).text)
    enddate = str(xml_soup.find(['xbrli:enddate','enddate']).text)

    start_date = datetime.date.fromisoformat(startdate)
    end_date = datetime.date.fromisoformat(enddate)

    if end_date.month - start_date.month < 4:
        period_type = 'Trimester'
        if start_date.month <= 2:
            period_number = 1
        elif start_date.month <= 4:
            period_number = 2
        elif start_date.month <= 7:
            period_number = 3
        elif start_date.month >= 9:
            period_number = 4
    elif end_date.month - start_date.month > 4:
        period_type = 'Semester'
        if start_date.month <= 2:
            period_number = 1
        elif start_date.month > 5:
            period_number = 2

    full_period = f'{period_type} {period_number} {start_date.year}'

    # datos generales
    registro_CNMV = int(xml_soup.find(['iic-com:registrocnmv','registrocnmv']).text)
    email_gest = xml_soup.find(['dgi-est-gen:communicationvalue','communicationvalue']).text
    rating_depos = xml_soup.find(['iic-com:ratingdepositario','ratingdepositario']).text
    riesgo = xml_soup.find(['iic-com:perfilriesgo','perfilriesgo']).text

    # "FIM_S22020_V-66247677_da"
    try: context_ref=xml_soup.find(["xbrli:context",'context'])['id']
    except:context_ref=f'FIM_{full_period[0]}{period_number}{start_date.year}_V-{nif}_da'
    context_ref2=f'{context_ref[:-2]}ia'
    context_ref3=f'{context_ref[:-2]}daq'
    context_ref_short = 'da'
    context_ref2_short = 'ia'
    context_ref3_short = 'daq'
    context_ref_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_da'
    context_ref2_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_ia'
    context_ref3_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_daq'

    context_ref_list = [context_ref, context_ref_short, context_ref_nodash]
    context_ref2_list = [context_ref2, context_ref2_short, context_ref2_nodash]
    context_ref3_list = [context_ref3, context_ref3_short, context_ref3_nodash]
    #         da: periodo actual
    #         ia: fin periodo?
    #         daq: quarter actual

    rotacion = xml_soup.find(['iic-com:indicerotacioncartera','indicerotacioncartera'], {'contextref': context_ref_list})
    rentab_avg = xml_soup.find(['iic-com:rentabilidadmedialiquidez','rentabilidadmedialiquidez'], {'contextref': context_ref_list})
    remun_liq=xml_soup.find(['iic-fic:remuneracionliquidezfic','remuneracionliquidezfic'], {'contextref': context_ref_list})
    n_participaciones = xml_soup.find(['iic-com-fon:numeroparticipaciones','numeroparticipaciones'], {'contextref': context_ref2_list})
    n_participes = xml_soup.find(['iic-com-fon:numeroparticipes','numeroparticipes'], {'contextref': context_ref2_list})
    beneficio = xml_soup.find(['iic-com-fon:beneficiobrutoparticipacion','beneficiobrutoparticipacion'], {'contextref': context_ref_list})
    dividendos = xml_soup.find(['iic-com:distribuyedividendos','distribuyedividendos'], {'contextref': context_ref_list})
    patrimonio = xml_soup.find(['iic-com:patrimonio','patrimonio'], {'contextref': context_ref2_list})
    valor_liq = xml_soup.find(['iic-com:valorliquidativo','valorliquidativo'], {'contextref': context_ref2_list})
    comision_gest_pat = xml_soup.find(['iic-com:comisiongestioncobradapatrimonio','comisiongestioncobradapatrimonio'], {'contextref': context_ref_list})
    comision_gest_res = xml_soup.find(['iic-com:comisiongestioncobradaresultados','comisiongestioncobradaresultados'], {'contextref': context_ref_list})
    comision_gest_total = xml_soup.find(['iic-com-fon:comisiongestioncobrada','comisiongestioncobrada'], {'contextref': context_ref_list})
    comision_depos = xml_soup.find(['iic-com-fon:comisiondepositariocobrada','comisiondepositariocobrada'], {'contextref': context_ref_list})

    # solo he cogido la del ultimo trimestre, rentabilidad extremas omitidas
    rentab_IIC_trim = xml_soup.find(['iic-com:rentabilidadiic','rentabilidadiic'], {'contextref': context_ref_list})
    if rentab_IIC_trim == None:
        rentab_IIC_trim = xml_soup.find(['iic-com:rentabilidadiic','rentabilidadiic'], {'contextref': context_ref3_list})

    # volatilidad de valor liquidativo, resto omitidas
    volat_vl_trim = xml_soup.find(['iic-com-fon:volatilidadvalorliquidativo','volatilidadvalorliquidativo'], {'contextref': context_ref_list, })
    if volat_vl_trim == None:
        volat_vl_trim = xml_soup.find(['iic-com-fon:volatilidadvalorliquidativo','volatilidadvalorliquidativo'], {'contextref': context_ref3_list})

    ratio_gastos_trim = xml_soup.find(['iic-com:ratiototalgastos','ratiototalgastos'], {'contextref': context_ref_list})
    if ratio_gastos_trim == None:
        ratio_gastos_trim = xml_soup.find(['iic-com:ratiototalgastos','ratiototalgastos'], {'contextref': context_ref3_list})

    float_vars = [rotacion, rentab_avg, remun_liq, n_participaciones, beneficio, valor_liq,
                  comision_gest_pat, comision_gest_res, comision_gest_total,
                  comision_depos, rentab_IIC_trim, volat_vl_trim, ratio_gastos_trim]
    int_vars = [n_participes, patrimonio]

    for k in range(len(float_vars)):
        fvar = float_vars[k]
        if fvar != None:
            float_vars[k] = float(fvar.text)
    rotacion, rentab_avg, remun_liq,n_participaciones, beneficio, valor_liq, comision_gest_pat, comision_gest_res, comision_gest_total, comision_depos, rentab_IIC_trim, volat_vl_trim, ratio_gastos_trim = float_vars

    for k in range(len(int_vars)):
        ivar = int_vars[k]
        if ivar != None:
            int_vars[k] = int(float(ivar.text))
    n_participes, patrimonio = int_vars

    try: dividendos = dividendos.text
    except: pass

    return {"fondo": fondo, "name": name, "nif": nif, "period": full_period,
            'start_date': start_date, 'end_date': end_date, 'registro_CNMV': registro_CNMV,
            'email_gest': email_gest, 'rating_depos': rating_depos, 'riesgo': riesgo,
            'rotacion': rotacion, 'rentab_avg': rentab_avg, 'remun_liq': remun_liq,
            'n_participaciones': n_participaciones, 'n_participes': n_participes,
            'beneficio': beneficio, 'patrimonio': patrimonio,
            'dividendos': dividendos, 'valor_liq': valor_liq,
            'comision_gest_pat': comision_gest_pat, 'comision_gest_res': comision_gest_res,
            'comision_gest_total': comision_gest_total, 'comision_depos': comision_depos,
            'rentab_IIC_trim': rentab_IIC_trim,
            'volat_vl_trim': volat_vl_trim, 'ratio_gastos_trim': ratio_gastos_trim}


def xml_scrap_clase(xml_soup, nif, fondo, i):
    class_name = xml_soup.find_all('iic-com:denominacionclase')[i].text
    # periodo
    startdate = str(xml_soup.find('xbrli:startdate').text)
    enddate = str(xml_soup.find('xbrli:enddate').text)

    start_date = datetime.date.fromisoformat(startdate)
    end_date = datetime.date.fromisoformat(enddate)

    if end_date.month - start_date.month < 4:
        period_type = 'Trimester'
        if start_date.month <= 2:
            period_number = 1
        elif start_date.month <= 4:
            period_number = 2
        elif start_date.month <= 7:
            period_number = 3
        elif start_date.month >= 9:
            period_number = 4
    elif end_date.month - start_date.month > 4:
        period_type = 'Semester'
        if start_date.month <= 2:
            period_number = 1
        elif start_date.month > 5:
            period_number = 2

    full_period = f'{period_type} {period_number} {start_date.year}'
    # general
    registro_CNMV = int(xml_soup.find('iic-com:registrocnmv').text)
    email_gest = xml_soup.find('dgi-est-gen:communicationvalue').text
    rating_depos = xml_soup.find('iic-com:ratingdepositario').text
    riesgo = xml_soup.find('iic-com:perfilriesgo').text

    # "FIM_S22020_V-66247677_da"
    try:context_ref=xml_soup.find("xbrli:context")['id']
    except:context_ref=f'FIM_{full_period[0]}{period_number}{start_date.year}_V-{nif}_da'
    context_ref2=f'{context_ref[:-2]}ia'
    context_ref3=f'{context_ref[:-2]}daq'
    context_ref_short = 'da'
    context_ref2_short = 'ia'
    context_ref3_short = 'daq'
    context_ref_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_da'
    context_ref2_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_ia'
    context_ref3_nodash = f'FIM_{period_type[0]}{period_number}{start_date.year}_V{nif}_daq'

    context_ref_list = [context_ref, context_ref_short, context_ref_nodash]
    context_ref2_list = [context_ref2, context_ref2_short, context_ref2_nodash]
    context_ref3_list = [context_ref3, context_ref3_short, context_ref3_nodash]
    #         da: periodo actual
    #         ia: fin periodo?
    #         daq: quarter actual
    rotacion = xml_soup.find('iic-com:indicerotacioncartera', {'contextref': context_ref_list})
    rentab_avg = xml_soup.find('iic-com:rentabilidadmedialiquidez', {'contextref': context_ref_list})
    remun_liq=xml_soup.find('iic-fic:remuneracionliquidezfic', {'contextref': context_ref_list})
    try:
        rotacion = float(rotacion.text)
    except: pass
    try:
        rentab_avg = float(rentab_avg.text)
    except: pass
    try:
        remun_liq = float(remun_liq.text)
    except: pass

    n_participaciones = xml_soup.find_all('iic-com-fon:numeroparticipaciones', {'contextref': context_ref2_list})
    n_participes = xml_soup.find_all('iic-com-fon:numeroparticipes', {'contextref': context_ref2_list})
    beneficio = xml_soup.find_all('iic-com-fon:beneficiobrutoparticipacion', {'contextref': context_ref_list})
    dividendos = xml_soup.find_all('iic-com:distribuyedividendos', {'contextref': context_ref_list})
    patrimonio = xml_soup.find_all('iic-com:patrimonio', {'contextref': context_ref2_list})
    valor_liq = xml_soup.find_all('iic-com:valorliquidativo', {'contextref': context_ref2_list})
    comision_gest_pat = xml_soup.find_all('iic-com:comisiongestioncobradapatrimonio', {'contextref': context_ref_list})
    comision_gest_res = xml_soup.find_all('iic-com:comisiongestioncobradaresultados', {'contextref': context_ref_list})
    comision_gest_total = xml_soup.find_all('iic-com-fon:comisiongestioncobrada', {'contextref': context_ref_list})
    comision_depos = xml_soup.find_all('iic-com-fon:comisiondepositariocobrada', {'contextref': context_ref_list})

    # solo he cogido la del ultimo trimestre, rentabilidad extremas omitidas
    rentab_IIC_trim = xml_soup.find_all('iic-com:rentabilidadiic', {'contextref': context_ref_list})
    if rentab_IIC_trim == None:
        rentab_IIC_trim = xml_soup.find_all('iic-com:rentabilidadiic', {'contextref': context_ref3_list})

    # volatilidad de valor liquidativo, resto omitidas
    volat_vl_trim = xml_soup.find_all('iic-com-fon:volatilidadvalorliquidativo', {'contextref': context_ref_list, })
    if volat_vl_trim == None:
        volat_vl_trim = xml_soup.find_all('iic-com-fon:volatilidadvalorliquidativo', {'contextref': context_ref3_list})

    ratio_gastos_trim = xml_soup.find_all('iic-com:ratiototalgastos', {'contextref': context_ref_list})
    if ratio_gastos_trim == None:
        ratio_gastos_trim = xml_soup.find_all('iic-com:ratiototalgastos', {'contextref': context_ref3_list})

    float_vars = [n_participaciones, beneficio, valor_liq,
                  comision_gest_pat, comision_gest_res, comision_gest_total,
                  comision_depos, rentab_IIC_trim, volat_vl_trim, ratio_gastos_trim]
    int_vars = [n_participes, patrimonio]

    for j in range(len(float_vars)):
        fvar = float_vars[j]
        if fvar != None:
            try: float_vars[j] = float(fvar[i].text)
            except: pass
    n_participaciones, beneficio, valor_liq, comision_gest_pat, comision_gest_res, comision_gest_total, comision_depos, rentab_IIC_trim, volat_vl_trim, ratio_gastos_trim = float_vars

    for j in range(len(int_vars)):
        ivar = int_vars[j]
        if ivar != None:
            try: int_vars[j] = int(float(ivar[i].text))
            except: pass
    n_participes, patrimonio = int_vars

    try: dividendos = dividendos[i].text
    except: pass

    return {"fondo": fondo, "name": class_name, "nif": nif, "period": full_period,
            'start_date': start_date, 'end_date': end_date, 'registro_CNMV': registro_CNMV,
            'email_gest': email_gest, 'rating_depos': rating_depos, 'riesgo': riesgo,
            'rotacion': rotacion, 'rentab_avg': rentab_avg, 'remun_liq':remun_liq,
            'n_participaciones': n_participaciones, 'n_participes': n_participes,
            'beneficio': beneficio, 'patrimonio': patrimonio, 'dividendos': dividendos, 'valor_liq': valor_liq,
            'comision_gest_pat': comision_gest_pat, 'comision_gest_res': comision_gest_res,
            'comision_gest_total': comision_gest_total, 'comision_depos': comision_depos,
            'rentab_IIC_trim': rentab_IIC_trim,
            'volat_vl_trim': volat_vl_trim, 'ratio_gastos_trim': ratio_gastos_trim}

def get_info_posiciones(fondo,link):
    pass