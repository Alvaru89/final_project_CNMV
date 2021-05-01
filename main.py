import argparse
import os
import p_acquisition.m_acquisition_lean as acq
import p_wrangling.m_wrangling as wra
import datetime

def argument_parser():
    """
    parse arguments to script
    """
    parser=argparse.ArgumentParser(description='pass csv file')
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
        try: acq.get_info_fondo(fondo,link)
        except Exception:
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
        #acq.get_info_posiciones(fondo,link)
        #print(f'Elapsed time: {(datetime.datetime.now() - a).total_seconds() / 60} minutes')


    print("building dataframe")
    df=wra.create_df()
    clean_df=wra.wrang_main(df)
    print("creating data")
    extra_df=wra.wrang_main(wra.create_data(df,merge=False,save=True))


if __name__ == '__main__':
    my_arguments= argument_parser()
    main(my_arguments)
    print('Pipeline finished')


