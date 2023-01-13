import pandas as pd
# import numpy as np
# import pyodbc 
import datetime
import sys



def main():

    # path where the python script for reading the data is located
    SCRIPT_PATH = r'O:\PARM\Corporate Actuarial\Reserving\Scripts\python\cin_re_data'
    
    # year, month, day
    today = datetime.datetime.today()
    y, m, d, hr, mi, se = today.year, today.month, today.day, today.hour, today.minute, today.second
    
    # output path for the returned data set
    OUTPUT_PATH = r'O:\PARM\Corporate Actuarial\Reserving\Assumed Reinsurance\data\DATA_FEED\v1_table'
    OUTPUT_FILENAME = 'cre_data_feed_{}_{}_{}_{}_{}_{}.xlsx'.format(y, m, d, hr, mi, se)
    OUTPUT_FILEPATH = '{}\\{}'.format(OUTPUT_PATH, OUTPUT_FILENAME)
    
    # add the path to the system PATH variable so it can be loaded 
    sys.path.append(SCRIPT_PATH)
    
    # import the script 
    import build_contract_layer_tables_20220202 as credat

    # connect to the various databases
    lc_conn, ds_conn, sap_conn, air_conn, rsv_conn = credat.connect_to_dbs()
    
    # pull the data set
    df = credat.join_layer_contract(lc_conn, ds_conn, sap_conn, air_conn)
    
    
    print('outputting data table to {}'.format(OUTPUT_FILEPATH))
    # output to OUTPUT_PATH
    df.to_excel(OUTPUT_FILEPATH)


main()