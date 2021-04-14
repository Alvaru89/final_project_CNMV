import argparse
import os
import p_acquisition.m_acquisition as acq
import p_wrangling.m_wrangling as wra
import p_analysis
import p_reporting

def argument_parser():
    """
    parse arguments to script
    """
    parser=argparse.ArgumentParser(description='pass csv file')
    #parser.add_argument("-c","--country", help='specify country or type all', type=str)
    #parser.add_argument("-b", "--bonus", help='specify bonus 1 or 2', type=str)
    parser.add_argument("-d", "--delete", help='specify Y or y', type=str)
    args=parser.parse_args()
    return args

def main(arguments):
    print("starting process")
    if arguments.delete != None:
        if arguments.delete.lower() == 'y':
            "cleaning existing data"
            for file in os.listdir("data/csv"):
                os.remove(f"data/csv/{file}")
            os.remove('data/dict_links.csv')
    print("obteniendo links de los fondos")
    if os.path.isfile('data/dict_links.csv'):
        dict_links=acq.get_links_from_csv()
    else:
        dict_links=acq.get_links_from_web()
    print("obteniendo informacion de los fondos")
    for fondo, link in dict_links.items():
        acq.get_info_fondo(fondo,link)
        acq.get_info_posiciones(fondo,link)


    print("building dataframe")
    df=wra.create_df()
    clean_df=wra.wrang_main(df)


if __name__ == '__main__':
    my_arguments= argument_parser()
    main(my_arguments)
    print(len(os.listdir('data/csv')))
    print('df created')


