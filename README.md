## Ironhack Data Analytics Final Project: 
# FondoAdvisor by Alvaro Rodriguez

## **Introduction and purpose**

This repository includes all the code I have used to develop [FondoAdvisor](www.tbd.com), a website to help prospective or current investors with their financial decisions.

The tool has a website created with streamlit, supported by a pipeline that extracts public information from investments funds from [link](https://www.cnmv.es/), treats the information and saves

## **Structure**

The pipeline is supported by 2 packages: p_acquisition and p_wrangling. Each package contains a module (script) including the functions to support the main script.

- On the acquisition package, the information is extracted from the CNMV. The extraction is done with requests library and BeautifulSoup. The extracted data is saved in csv files in the 'data' folder:

    - General fund information is in 'data/csv_gen_info' e.g. fund investment group, depositary, depositary rating...
    - The historical financial information is stored in 'data/csv' e.g. profitability, risk, rotation, fees,...
    
    
- On the wrangling package, the dataframe is built, cleaned and treated. New data is also generated to improve the visualization (stored in 'data/created_data').

The front-end is a website created using Streamlit and hosted in Amazon Web Services. The main Streamlit script is supported by separate scripts, stored in 'front_end' folder. For AWS hosting, I used this [tutorial](https://towardsdatascience.com/how-to-deploy-a-streamlit-app-using-an-amazon-free-ec2-instance-416a41f69dc3) but there are many more.

The folder 'notebooks' includes jupyter notebooks used for development phase, but with no current use.

The script 'playgrounds' is a light version of the pipeline when only a subset of the funds is required. The list of funds to download has to be written as a list in the variable 'fondos'

## **How to use it**

If you want to download data from CNMV, you just need to run the main.py script with your Python launcher.

There are some optional arguments that can be used:
    
    -d or --delete: when given the values 'Y' or 'y' all the files in the data folder will be deleted to do a clean download.*  
*If non-supported values are provided, ValueError is raised, except for delete argument, which ignores the input and no files will be deleted.

The pipeline includes a Telegram alert via bot, but you will need to create your own bot since the bot keys are not added. I used this [tutorial](https://core.telegram.org/bots#:~:text=Use%20the%20%2Fnewbot%20command%20to,mentions%20and%20t.me%20links.) but there are many more.

If you want to run the streamlit server, you need to run the main_streamlit.py with your Python launcher. The website includes 3 tools:

- **_Comparador de fondos_**: allows easy comparison of different investment funds and their main variables.

- **_¿Cuánto habría ganado si...?_**: provides the current value of an investment that you could have made in a specific fund in the past.

- **_Top 5 fondos_**: provides the top 5 funds, ranked by profitability in a specific period. Please be patient since it needs to load all the database. It  will only take 2-3 minutes.

## **Libraries used**
- [argparse](https://docs.python.org/3/library/argparse.html): for passing arguments on command line
- [os](https://docs.python.org/3/library/os.html): for interaction with the operating system: directories and files.
- [Pandas](https://pandas.pydata.org/pandas-docs/stable/index.html): for data treatment
- [requests](https://requests.readthedocs.io/en/master/): for api and html queries
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): for webscraping the html code
- [datetime](https://docs.python.org/3/library/datetime.html): to work with date values
- [tqdm](https://tqdm.github.io/): for progress visualization
- [Streamlit](https://docs.streamlit.io/en/stable/): to create the website
- [Altair](https://altair-viz.github.io/): for some special visualizations in Streamlit.
- [Telegram](https://core.telegram.org/bots): to get an alert when the script has stopped
