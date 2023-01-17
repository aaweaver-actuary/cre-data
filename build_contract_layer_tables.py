import pandas as pd
import numpy as np
import pyodbc
import datetime

db_list = ['CINRE_LC', 'CINRE_DealSheet', 'CINRE_SAP',
           'CINRE_PRICING_AIRv10', 'CorpAct_Reserving']


def constr(
        database_name: str,
        server_name: str = "Corpsqlhqpcf060\HS1,4911",
        driver_name: str = "SQL Server", trusted_connection:
        str = "yes") -> str:
    """
    # Description: 
        Function to build the connection string for the database

    # Parameters:
        database_name:
            string, name of the database (e.g. 'CINRE_LC')
        server_name:
            string, name of the server (e.g. 'Corpsqlhqpcf060\HS1,4911')
            default: "Corpsqlhqpcf060\HS1,4911"
        driver_name:
            string, name of the driver (e.g. 'SQL Server')
            default: "SQL Server"
        trusted_connection:
            string, name of the trusted connection (e.g. 'yes')
            default: "yes"

    # Output:
        connection string for the database
        of the form:

    # Example:
        constr('CINRE_LC')
        > 'Driver={SQL Server};Server=Corpsqlhqpcf060\HS1,4911;
           Database=CINRE_LC;Trusted_Connection=yes;'

        constr("CorpAct_Reserving", "different_server", "Fake Driver", "no")
        > 'Driver={Fake Driver};Server=different_server;
           Database=CorpAct_Reserving;Trusted_Connection=no;'
    """
    # return the connection string
    return (r'Driver={};'r'Server={};'r'Database={};'r'Trusted_Connection={};'
            .format(driver_name, server_name, database_name, trusted_connection))


def connect_to_dbs(*args: str) -> dict(str, pyodbc.Connection):
    """
    # Description:
        Function that takes an arbitrary number of database names and returns
        a dictionary of connection strings whose keys are the database names and
        whose values are the connection strings

        If no arguments are passed, the function will use the global variable db_list
        as the list of databases to connect to

    # Parameters:
        args:
            string, name of the database (e.g. 'CINRE_LC')

    # Output:
        dictionary of connection strings for the databases
        of the form:
            {'CINRE_LC': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_DealSheet': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_SAP': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_PRICING_AIRv10': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CorpAct_Reserving': <pyodbc.Connection object at 0x0000020B1B0F0C88>}

    # Example:
        connect_to_dbs()
        > {'CINRE_LC': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_DealSheet': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_SAP': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_PRICING_AIRv10': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CorpAct_Reserving': <pyodbc.Connection object at 0x0000020B1B0F0C88>}

        connect_to_dbs('CINRE_LC', 'CINRE_DealSheet')
        > {'CINRE_LC': <pyodbc.Connection object at 0x0000020B1B0F0C88>,
            'CINRE_DealSheet': <pyodbc.Connection object at 0x0000020B1B0F0C88>}
        """

    # if no arguments are passed, use the global variable db_list
    if len(args) == 0:
        args = db_list

    # loop through the args and build the dictionary
    return {x: pyodbc.connect(constr(x)) for x in args}


def readtbl(table_name: str, conn: pyodbc.Connection) -> pd.DataFrame:
    """
    # Description:
        Function that takes a table name and a connection object and returns a dataframe
        containing the data from the table

    # Parameters:
        table_name:
            string, name of the table (e.g. 'CINRE_LC.dbo.CINRE_LC')
        conn:
            pyodbc.Connection object, connection to the database

    # Output:
        dataframe containing the data from the table

    # Example:
        # assume the table CINRE_LC.dbo.CINRE_LC exists in the database CINRE_LC
        # and is 3 rows two columns with A, B, C, D, E, F as the data and the columns
        # are named col1 and col2
        conn = connect_to_dbs()['CINRE_LC']
        readtbl('CINRE_LC.dbo.CINRE_LC', conn)
        >  col1 col2
        0    A    B
        1    C    D
        2    E    F
    """
    # read the table into a dataframe using the connection
    return pd.read_sql_query('select * from [{}]'.format(table_name), conn)


def build_timestamp(nearest: int = 10) -> datetime.datetime:
    """
    # Description:
        Function that takes a number of minutes and returns a timestamp rounded to the nearest
        number of minutes. The default is 10 minutes.

    # Parameters:
        nearest:
            int, number of minutes to round to (e.g. 10)
            default: 10

    # Output:
        timestamp rounded to the nearest number of minutes

    # Example:
        # assume the time is 10:03:00, on 3/2/2027
        build_timestamp()
        > datetime.datetime(2027, 3, 2, 10, 0) # 10:00:00 is the nearest 10 minutes
    """
    # build the timstamp for when the data are pulled rounded to 10 minutes
    # this is done by:
    # subtracting the current time from
    # the minimum time and then
    # rounding to the nearest 10 minutes
    now = datetime.datetime.now()
    return (now - (now - datetime.datetime.min) % datetime.timedelta(minutes=nearest))


def raw_lookup_tbl(
        df: pd.DataFrame,
        id_col_name: str,
        col_list: list,
        nearest: int = 10) -> pd.DataFrame:
    """
    # Description:
        Function that takes a dataframe, a column name, and a list of columns and returns a dataframe
        containing the unique values of the columns in the list and the index of the unique values
        in the column name

    # Parameters:
        df:
            dataframe, dataframe containing the data
        id_col_name:
            string, name of the column to use as the index
        col_list:
            list, list of columns to use as the values

    # Output:
        dataframe containing the unique values of the columns in the list and the index of the unique values
        in the column name. this is used to build lookup tables and set up a star schema so that the
        data can be normalized

    # Example:
        # assume the dataframe df is 3 rows two columns first A, A, A, B, B, B, second 1,2,3,4,5,6, 
        # and third X1, X2, X3, X3, X2, X1
        # with columns named col1, col2, col3
        raw_lookup_tbl(df, 'col1_id', ['col1'])
        >   timestamp col1_id col1
        0 2020-03-02       0    A
        1 2020-03-02       1    B

        raw_lookup_tbl(df, 'col3_id', ['col3'])
        >   timestamp col3_id col3  
        0 2020-03-02       0    X1
        1 2020-03-02       1    X2
        2 2020-03-02       2    X3
    """

    # build the lookup table for the column names
    col_df = (
        # select the columns in the `col_list`
        df[col_list]

        # drop duplicates, sort, reset the index, and rename the index
        .drop_duplicates()
        .sort_values(col_list)
        .reset_index(drop=True)
        .reset_index()
        .rename(columns=dict(index=id_col_name))
    )

    # build the timstamp for when the data are pulled rounded to
    # `nearest` minutes using `build_timestamp()`
    col_df['timestamp'] = build_timestamp(nearest=nearest)

    # reorder columns so that timestamp is first
    col_df = col_df[['timestamp', id_col_name] + col_list]

    # return the dataframe
    return (col_df)


def raw_lookup_dict(
        df: pd.DataFrame, id_col_names: list, col_lists: list) -> dict:
    """
    # Description:
        Function that takes a dataframe, a list of column names, and
        a list of lists of columns and returns a dictionary containing
        the unique values of the columns in the list and the index of
        the unique values in the column name for each column name

    # Parameters:
        df:
            dataframe, dataframe containing the data
        id_col_names:
            list, list of column names to use as the index
        col_lists:
            list, list of lists of columns to use as the values

    """
    # initialize the output dictionary
    out = {}

    # loop through the column names and build the lookup table:
    # note that zip() is used to loop through two lists at the same time
    for id_col, cols in zip(id_col_names, col_lists):
        out[id_col] = raw_lookup_tbl(df=df, id_col_name=id_col, col_list=cols)

    # return the dictionary
    return (out)


def all4hierarchy(*args: pd.Series) -> pd.Series:
    """
    # Description:
        Function that takes an arbitrary number of series and
        returns a series with the first non-null value from the 
        series

    # Parameters:
        *args:
            pd.Series, series to use to build the hierarchy

    # Output:
        pd.Series, series with the first non-null value from the
        series

    # Example:
        # assume the series are:
        # ds: Null, 2, 3, 4, 5, 6, 7, 8, 9, 10
        # lc: Null, 2, 3, 4, 5, 6, 7, 8, 9, 10
        # air: 2, 2, 3, 4, 5, 6, 7, 8, 9, 10
        # sap: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 
        all4hierarchy(ds, lc, air, sap)
        > 0     2
    """
    # build the dataframe from the series
    # example: if we have 4 series, ds, lc, air, sap, then
    # df = pd.DataFrame(dict(ds=ds, lc=lc, air=air, sap=sap))
    # we can use the *args to do this as well, and it is more
    # flexible. use the zip() function to build the dictionary
    # and the dict() function to build the dataframe
    df = pd.DataFrame(dict(zip(args)))

    # filter the dataframe to get the first non-null value
    # with an effect similar to the COALESCE function in SQL
    # use apply to get the first non-null value, using the `first_valid_index()`
    # method, that comes from the pandas documentation
    return (df.apply(lambda x: x.first_valid_index(), axis=1))


def cinre_lc_contract(
        lc_conn: pyodbc.Connection,
        earliest_inception: str = '2020-01-01') -> pd.DataFrame:
    """
    # Description:
        Function that reads in the contract table from the loss cost database

    # Parameters:
        lc_conn:
            pyodbc.Connection, connection to the loss cost database
        earliest_inception:
            string, earliest inception date to use in the query
            must be in the format 'YYYY-MM-DD'
            default is '2020-01-01'

    # Output:
        dataframe, dataframe containing the contract table from the loss cost database

    # Example:
        cinre_lc_contract(lc_conn)
        >   CrmGroupID MgtRptLine  ... LossEvalDate crm_id_lc
        0       10000          1  ...   2020-01-01         0
        1       10000          2  ...   2020-01-01         1
        2       10000          3  ...   2020-01-01         2
        3       10000          4  ...   2020-01-01         3
        ...       ...        ...  ...          ...       ...
    """
    # print statement that the function is running
    print('reading Contract table from loss cost DB')

    # read in table
    contract_lc = readtbl("Contract", lc_conn)

    # recode date columns to datetime
    contract_lc[['Inception', 'Expiration', 'LossEvalDate']] = contract_lc[
        'Inception Expiration LossEvalDate'.split()].apply(pd.to_datetime)

    # we only take inception dates after the `earliest_inception` date
    contract_lc = contract_lc.loc[contract_lc.Inception >= datetime.datetime.fromisoformat(
        earliest_inception), :].reset_index(drop=True)

    # add in CRM_ID, which is a combination of CrmGroupID and MgtRptLine
    # which takes the first character of CrmGroupID and adds MgtRptLine
    contract_lc['crm_id_lc'] = contract_lc['CrmGroupID MgtRptLine'.split()].apply(
        lambda x: x[1][0] + str(x[0]), axis=1)

    # change column names to be more descriptive, and add in the `_lc` suffix
    # to indicate that the column comes from the loss cost database
    # these are the current column names:
    contract_lc_curcols = ['CrmGroupID', 'Account', 'MgtRptLine', 'Description', 'Program', 'Inception', 'Expiration', 'TreatyBasis',
                           'AlaeBasis', 'LossEvalDate', 'Status', 'CatModelVersion', 'Note', 'UserID', 'LastUpdated', 'Region', 'Currency', 'SourceFile']
    contract_lc_newcols = ['crm_gp_id', 'account', 'mrl', 'account_desc', 'program', 'eff_date', 'exp_date', 'treaty_basis', 'alae_basis',
                           'loss_eval_date', 'status', 'cat_model_version', 'note', 'user_id', 'last_updated', 'region', 'currency', 'source_file']
    contract_lc.rename(columns=dict(zip(contract_lc_curcols, [
                       c + '_lc' for c in contract_lc_newcols])), inplace=True)

    # filter out declined statuses, as well as WIP and NTU
    lc_stats_to_filter_out = ['Declined', 'DECLINED', 'declined',
                              'Decline', 'DECLINE', 'decline', 'wip', 'WIP', 'Wip', 'ntu', 'NTU']
    contract_lc = contract_lc.query('status_lc != @lc_stats_to_filter_out')

    # return table
    return (contract_lc)


def cinre_dealsheet_contract(ds_conn: pyodbc.Connection, earliest_inception: str = '2020-01-01') -> pd.DataFrame:
    """
    # Description:
        Function that reads in the contract table from the deal sheet database

    # Parameters:
        ds_conn:
            pyodbc.Connection, connection to the deal sheet database
        earliest_inception:
            string, earliest inception date to use in the query
            must be in the format 'YYYY-MM-DD'
            default is '2020-01-01'

    # Output:
        pd.DataFrame, dataframe containing the contract table from the deal sheet database

    # Example:
        cinre_dealsheet_contract(ds_conn)
        >   CinReId CRMID  ... DominantType timestamp_ds
        0        1     0  ...         None   2020-01-01
        1        2     1  ...         None   2020-01-01
        2        3     2  ...         None   2020-01-01
        ...      ...   ...  ...          ...          ...
    """
    # print statement that the function is running

    print('reading Contract table from deal sheet DB')

    # read in table using `readtbl` function
    contract_ds = readtbl("Contract", ds_conn)

    # recode date columns to datetime
    # the most efficient way to do this is to use a list comprehension:
    contract_ds[['Inception', 'Expiration', 'LastUpdated']] = [pd.to_datetime(
        contract_ds[c]) for c in 'Inception Expiration LastUpdated'.split()]

    # but this is not as readable, so we will include this method for reference:
    # for c in 'Inception Expiration LastUpdated'.split():
    #     contract_ds[c] = pd.to_datetime(contract_ds[c])

    # we only take inception dates after the `earliest_inception` date
    contract_ds = contract_ds.loc[contract_ds.Inception >= datetime.datetime.fromisoformat(
        earliest_inception), :].reset_index(drop=True)

    # change column names to be more descriptive, and add in the `_ds` suffix
    # to indicate that the column comes from the deal sheet database
    # these are the current column names:
    contract_ds_curcols = ['CinReId', 'CRMID', 'ClientName', 'Reassured', 'Inception', 'Expiration', 'ContractName', 'DominantType', 'MGA', 'Broker', 'BrokerNum', 'TreatyCategory', 'Line', 'UltCinRePrem', 'ExpectedLoss', 'ExpenseRatio', 'TechUWRatio', 'UWProfit', 'NPVUWProfit', 'ChgRateAdequacy', 'ROEChange',
                           'RateChange', 'ProgramRateChange', 'StandaloneTVaR250', 'StandaloneROC250', 'DiversifiedTVaR250', 'DiversifiedROC250', 'LossCV', 'Status', 'SourceFile', 'SharePointFile', 'Note', 'LastUpdated', 'CyberExposure', 'CyberAggLimit', 'Subline', 'CompanyID', 'DepositPrem', 'ModelExpectedLoss', 'AnnualValues']

    # these are the new column names:
    contract_ds_newcols = ['crm_gp_id', 'crm_id', 'client_name', 'reassured', 'eff_date', 'exp_date', 'contract_name', 'dominant_type', 'mga', 'broker', 'broker_numb', 'treaty_category', 'line', 'ult_cre_prem', 'expected_loss', 'expense_ratio', 'tech_uw_ratio', 'uw_profit', 'npv_uw_profit', 'chg_rate_adequacy', 'roe_change',
                           'rate_change', 'program_rate_change', 'standalone_tvar_250', 'standalone_roc_250', 'diversified_tvar_250', 'diversified_roc_250', 'loss_cv', 'status', 'source_file', 'share_point_file', 'note', 'last_updated', 'cyber_exposure', 'cyber_agg_limit', 'subline', 'company_id', 'deposit_prem', 'model_expected_loss', 'annual_values']

    # rename the columns
    contract_ds.rename(columns=dict(zip(contract_ds_curcols, [
                       c + '_ds' for c in contract_ds_newcols])), inplace=True)

    # want to bring in some columns from the `Layer` table, but we need to rename them
    # so that they don't conflict with the column names in the `contract_ds` table

    # define the dictionary that will be used to rename the columns:
    layer_rename = dict(
        CinReId='crm_gp_id_ds',
        Inception='eff_date_ds',
        Expiration='exp_date_ds',
        Trigger='trigger_ds',
        ContractType='contract_type_ds',
        Currency='currency_ds',
        Territory='terr_ds')

    # read in the `Layer` table, only keep the columns we need, rename them, and drop duplicates
    layer = (readtbl('Layer', ds_conn)[list(layer_rename.keys())]

             # rename columns & drop duplicates
             .rename(columns=layer_rename)
             .drop_duplicates())

    # recode date columns to datetime as above
    layer[['eff_date_ds', 'exp_date_ds']] = [
        pd.to_datetime(layer[c]) for c in 'eff_date_ds exp_date_ds'.split()]

    # merge the `contract_ds` and `layer` tables, using the `crm_gp_id_ds`,
    # `eff_date_ds`, and `exp_date_ds` columns
    contract_ds = contract_ds.merge(
        layer, how='left', on='crm_gp_id_ds eff_date_ds exp_date_ds'.split())

    # return table
    return (contract_ds)


def cinre_air_contract(air_conn: pyodbc.Connection, earliest_inception: str = "2020-01-01") -> pd.DataFrame:
    """
    # Description
        Read in the `Contract` table from the AIR database, and return it as a pandas DataFrame.

    # Parameters
        air_conn: pyodbc.Connection
            Connection to the AIR database.
        earliest_inception: str
            Earliest inception date to include in the returned table.
            Must be in ISO format (e.g. '2020-01-01').

    # Output
        contract_air: pd.DataFrame
            `Contract` table from the AIR database.

    # Example
        >>> contract_air = cinre_air_contract(air_conn)
        >>> contract_air.head()
        #  client_name client_id_numb   eff_date   ... crm_gp_id template_source
        # 0  Client 1        1234567 2020-01-01   ...  1234567   template name
        # 1  Client 2        2345678 2020-01-01   ...  2345678   template name
        # 2  Client 3        3456789 2020-01-01   ...  3456789   template name
        # 3  Client 4        4567890 2020-01-01   ...  4567890   template name
        # 4  Client 5        5678901 2020-01-01   ...  5678901   template name
        # [5 rows x 25 columns]
    """

    # print status message
    print('reading Contract table from AIR DB')

    # list of new column names
    air_new_cols = ['client_name', 'client_id_numb', 'eff_date', 'exp_date',
                    'program', 'crm_gp_id2', 'wp_contract', 'occ_limit_contract', 'agg_limit_contract',
                    'status', 'region', 'note', 'last_updated', 'has_pc', 'user_name', 'file_location',
                    'broker', 'executive_summary', 'currency', 'crm_id', 'fx_rate_id', 'template_altered',
                    'crm_gp_id', 'template_source']

    # list of statuses to exclude
    air_status_excl = ["Not Bound", "reference", "not bound",
                       "Declined", "wip", "Wip", "NTU", "ntu", "started"]

    # read in table
    contract_air = readtbl('Contract_New', air_conn)

    # rename columns
    contract_air.rename(columns=dict(zip(contract_air.columns.tolist(), [
                        c + '_air' for c in air_new_cols])), inplace=True)

    # recode dates using the `pd.to_datetime` function
    # for c in ['eff_date_air', 'exp_date_air']:
    #     contract_air[c] = pd.to_datetime(contract_air[c])
    contract_air[['eff_date_air', 'exp_date_air']] = [pd.to_datetime(
        contract_air[c]) for c in 'eff_date_air exp_date_air'.split()]

    # drop rows with dates before `earliest_inception`
    contract_air = contract_air.loc[contract_air.eff_date_air >=
                                    datetime.datetime.fromisoformat(earliest_inception), :]

    # drop some columns I don't want to carry forward
    colstodrop = ['crm_gp_id2_air', 'wp_contract_air', 'occ_limit_contract_air', 'agg_limit_contract_air',
                  'template_altered_air', 'has_pc_air', 'fx_rate_id_air', 'template_source_air']
    contract_air.drop(columns=colstodrop, inplace=True)

    # drop treaties not bound
    contract_air = contract_air.query('status_air != @air_status_excl')

    # return table
    return (contract_air)

# RESTART HERE


def cinre_sap_contract(sap_conn: pyodbc.Connection, earliest_date: str = "2020-01-01") -> pd.DataFrame:
    """
    # Description
        Read in the `Contract` table from the SAP database, and return it as a pandas DataFrame.

    # Parameters
        sap_conn: pyodbc.Connection
            Connection to the SAP database.
        earliest_date: str
            Earliest inception date to include in the returned table.
            Must be in ISO format (e.g. '2020-01-01').
            Default is '2020-01-01' (this is about the earliest date that
            the data quality is good enough to use).
    
    # Output
        contract_sap: pd.DataFrame
            `Contract` table from the SAP database.

    # Example
        >>> contract_sap = cinre_sap_contract(sap_conn)
        >>> contract_sap.head()
        #  Company Code Deal Number Contract Number  ... Cancel Date End of Acct Period
        # 0         1000  1000000001      1000000001  ...  2020-12-31         2020-12-31
        # 1         1000  1000000002      1000000002  ...  2020-12-31         2020-12-31
        # 2         1000  1000000003      1000000003  ...  2020-12-31         2020-12-31
        # 3         1000  1000000004      1000000004  ...  2020-12-31         2020-12-31
        # 4         1000  1000000005      1000000005  ...  2020-12-31         2020-12-31
        # [5 rows x 16 columns]
    """

    # print status message so I know it's working
    print('reading Contract table from SAP DB')

    # read in table from the SAP database
    contract_sap = readtbl(['Treaty$', sap_conn])

    # filter inception date to be after `earliest_date`
    contract_sap = contract_sap.loc[contract_sap['Effective Date'] >=
                                    datetime.datetime.fromisoformat(earliest_date), :].reset_index(drop=True)

    # change column names to be easier to work with (eg remove spaces) and make them lowercase, and add `_sap` to the end to compare 
    # with different databases that in theory have the same values
    contract_sap_curcols = ['Company Code', 'Deal Number', 'Contract Number', 'CRM Submission ID', 'Treaty Text', 'Cedent', 'Cedent Name', 'Underwriter for Treaty', 'Nature of Treaty', 'Treaty Category', 'Accounting Freq# No#', 'Account Level', 'Cancel Date', 'End of Acctg Year', 'Spec# Retro Allowed', 'Specific Retro Treaty', 'Effective Date', 'Expiration Date', 'Contract Status', 'Renewal', 'Exposure Territory', 'Retro Treaty Number', 'Retro Section Number', 'Cession Percentage', 'Reported Data Placement %', 'CinciRe Share/participation', 'Section', 'Text for Section', 'Contract Type', 'Layer', 'UW Area', 'Business Type Number', 'Contract Trigger', 'Cancel Type', 'Days Runoff', 'XPL Limit', 'ECO Limit', 'Peril',
                            'COB(UOBG)', 'CoB (UOBG) %', 'Segment', 'Subsegment', 'Quota Share %', 'Maximum Liability', 'Retained Line', 'No# of Lines', 'Limit', 'Retention', 'Cat Occurrence Retention', 'Cat Occurrence Limit', 'Terror Occurrence Limit', 'AAD', 'AAL', 'Loss Corridor Floor', 'Loss Corridor Ceiling', 'ALAE Treatment', 'Protected Share', 'Subject Premium', 'Base Rate', 'Min Rate for swing', 'Max Rate for swing', 'Deposit Premium', 'Reinstatement Cover %', 'Reinstatem# Time %', 'Flat Commission%', 'Provisional Commission%', 'Overriding Commission%', 'Brokerage%', 'Provisional Loss Ratio', 'Dev Pattern', 'LR at Min Commission', 'LR at Max Commission', 'Commission at Min', 'Commission at Max', 'Profit Commission %', 'Profit Commission Expense']
    contract_sap_newcols = ['company_code', 'deal_numb', 'contract_numb', 'crm_id', 'treaty_text', 'cedent', 'cedent_name', 'uw_for_treaty', 'nature_of_treaty', 'treaty_category', 'acct_freq_numb', 'acct_level', 'cancel_date', 'end_of_acct_year', 'specific_numb_retro_allowed', 'specific_retro_treaty', 'eff_date', 'exp_date', 'contract_status', 'renewal', 'exposure_terr', 'retro_treaty_numb', 'retro_section_numb', 'cession_pct', 'reported_data_placement_pct', 'cre_share_participation', 'section', 'text_for_section', 'contract_type', 'layer', 'uw_area', 'business_type_numb', 'contract_trigger', 'cancel_type', 'days_runoff', 'xpl_limit', 'eco_limit',
                            'peril', 'uobg', 'uobg_pct', 'segment', 'subsegment', 'qs_pct', 'max_liab', 'retained_line', 'number_of_lines', 'limit', 'retention', 'cat_occ_retention', 'cat_occ_limit', 'terror_occ_limit', 'aad', 'aal', 'loss_corridor_floor', 'loss_corridor_ceiling', 'alae_treatment', 'protected_share', 'subject_prem', 'base_rate', 'min_rate_for_swing', 'max_rate_for_swing', 'deposit_prem', 'reinstatement_cover_pct', 'reinstatement_time_pct', 'flat_comm_pct', 'provisional_comm_pct', 'overriding_comm_pct', 'brokerage_pct', 'provisional_loss_ratio', 'dev_pattern', 'lr_at_min_comm', 'lr_at_max_comm', 'comm_at_min', 'comm_at_max', 'profit_comm_pct', 'profit_comm']
    contract_sap.rename(columns=dict(zip(contract_sap_curcols, [
                        c + '_sap' for c in contract_sap_newcols])), inplace=True)

    # drop these columns that are more "layer" than "contract"
    contract_sap = contract_sap.drop('limit_sap retention_sap'.split(), 1)

    # drop these columns that are use numbers that I have found may not be correct
    contract_sap = contract_sap.drop('uobg_sap uobg_pct_sap layer_sap section_sap text_for_section_sap base_rate_sap min_rate_for_swing_sap max_rate_for_swing_sap reinstatement_cover_pct_sap reinstatement_time_pct_sap flat_comm_pct_sap provisional_comm_pct_sap overriding_comm_pct_sap brokerage_pct_sap provisional_loss_ratio_sap lr_at_min_comm_sap lr_at_max_comm_sap comm_at_min_sap comm_at_max_sap profit_comm_pct_sap profit_comm_sap cat_occ_retention_sap cat_occ_limit_sap terror_occ_limit_sap aad_sap aal_sap subject_prem_sap cedent_sap cedent_name_sap contract_status_sap'.split(), 1)
    contract_sap = contract_sap.drop(
        'deposit_prem_sap cre_share_participation_sap max_liab_sap segment_sap subsegment_sap contract_numb_sap treaty_text_sap contract_type_sap deal_numb_sap qs_pct_sap retained_line_sap number_of_lines_sap uw_area_sap'.split(), 1)
    contract_sap = contract_sap.drop(
        'retro_treaty_numb_sap retro_section_numb_sap cession_pct_sap reported_data_placement_pct_sap days_runoff_sap renewal_sap contract_trigger_sap alae_treatment_sap treaty_category_sap dev_pattern_sap xpl_limit_sap eco_limit_sap loss_corridor_floor_sap loss_corridor_ceiling_sap protected_share_sap'.split(), 1)
    contract_sap = contract_sap.drop_duplicates()
    contract_sap = contract_sap.reset_index(drop=True)

    # return table
    return (contract_sap)


def raw_contracts(lc_conn : pyodbc.Connection,
    ds_conn: pyodbc.Connection,
    sap_conn: pyodbc.Connection,
    air_conn: pyodbc.Connection,
    delete_once_renamed: bool = False ) -> pd.DataFrame:
    """
    # Description
    This function builds the raw contracts table from the individual contract tables.
    Reads data from the `Contracts` table (or similar) from four specific databases:
    - Loss Cost
    - Deal Sheet
    - SAP
    - AIR
    
    # Parameters 
    Note that all these connections are made in the above functions.  

    lc_conn: pyodbc.Connection
        Connection to the loss cost database.
    ds_conn: pyodbc.Connection
        Connection to the deal sheet database.
    sap_conn: pyodbc.Connection
        Connection to the SAP database.
    air_conn: pyodbc.Connection
        Connection to the AIR database.
    delete_once_renamed: bool
        If True, the columns that are compared to get the final column names are deleted.
        This is useful if you want to save memory, and should be implemented in the future.
        For now, it is set to False, and the columns are not deleted, so that the user can
        see the columns that were used to get the final column names and make sure they are
        correct.

    # Returns
    contract: pd.DataFrame
        The raw contracts table.

    # Example
    >>> contract = raw_contracts(lc_conn, ds_conn, sap_conn, air_conn)
    >>> contract.head()
    # crm_id_lc eff_date_lc crm_id_ds eff_date_ds crm_id_sap eff_date_sap crm_id_air eff_date_air
    .............................................

    """

    # build individual contract tables
    # tables are built from the individual contract tables
    # from each individual database
    contract_lc = cinre_lc_contract(lc_conn)
    contract_ds = cinre_dealsheet_contract(ds_conn)
    contract_sap = cinre_sap_contract(sap_conn)
    contract_air = cinre_air_contract(air_conn)

    # merge the contract tables together
    # this is done by joining on the `crm_id` and `eff_date` fields
    # these have been the most reliable fields in my brief testing
    print('joining contract tables from each database on crm_id and eff_date...')
    contract = (
                # loss cost database: crm_id_lc, eff_date_lc
                contract_lc

                # deal sheet database: crm_id_ds, eff_date_ds
                .merge(contract_ds, how='outer', left_on='crm_id_lc eff_date_lc'.split(), right_on='crm_id_ds eff_date_ds'.split())

                # sap database: crm_id_sap, eff_date_sap
                .merge(contract_sap, how='outer', left_on='crm_id_ds eff_date_ds'.split(), right_on='crm_id_sap eff_date_sap'.split())

                # air database: crm_id_air, eff_date_air
                .merge(contract_air, how='outer', left_on='crm_id_ds eff_date_ds'.split(), right_on='crm_id_air eff_date_air'.split())
                )

    # update the user that the join is complete
    print('updating contract table columns')
    
    # add timestamp column
    contract['timestamp'] = build_timestamp()

    # add columns for a join to contract table
    # this is done using the `all4hierarchy` function, which is designed to
    # take the values from the four databases and return the first non-null value
    # in this order:
    # 1. loss cost
    # 2. deal sheet
    # 3. air
    # 4. sap
    # this order is fairly arbitrary, but I have found that the loss cost database
    # is the most reliable, so I have placed it first, followed by the deal sheet,
    # air, and sap
    # note also that the columns start as names with the database name, and are then
    # renamed to the final column name
    contract['crm_gp_id'] = all4hierarchy(ds=contract.crm_gp_id_ds, lc=contract.crm_gp_id_lc, air=contract.crm_gp_id_air, sap=[
                                          0 for r in range(contract.shape[0])]).astype(int)
    contract['crm_id'] = all4hierarchy(ds=contract.crm_id_ds, lc=contract.crm_id_lc, air=contract.crm_id_air, sap=[
                                       'M0' for r in range(contract.shape[0])])
    contract['eff_date'] = all4hierarchy(ds=contract.eff_date_ds, lc=contract.eff_date_lc, air=contract.eff_date_air, sap=[
                                         datetime.datetime.fromisoformat('2200-12-31') for r in range(contract.shape[0])])
    contract['exp_date'] = all4hierarchy(ds=contract.exp_date_ds, lc=contract.exp_date_lc, air=contract.exp_date_air, sap=[
                                         datetime.datetime.fromisoformat('2201-12-31') for r in range(contract.shape[0])])

    # convert dates to datetime
    for c in 'eff_date exp_date'.split():
        contract[c] = pd.to_datetime(contract[c])

    # In this next portion, I am using the `all4hierarchy` function to
    # return the first non-null value from the four databases in the above order,
    # and then renaming the columns to the final column names
    # If the `delete_once_renamed` parameter is set to True, then the columns
    # that are used to get the final column names are deleted, to save memory

    # build `client_name`
    contract['client_name'] = all4hierarchy(
        ds=contract.client_name_ds, lc=contract.client_name_air, air=contract.account_lc, sap=contract.reassured_ds)

    # delete all four input columns if `delete_once_renamed` is True
    if delete_once_renamed:
        contract = contract.drop(columns='client_name_ds client_name_air account_lc reassured_ds'.split())

    # build `mrl` first by getting the `mrl` from the `crm_id` column
    contract['crm_id_mrl'] = contract.crm_id.apply(lambda x: x[0]).map(
        {'C': 'Casualty', 'P': 'Property', 'S': 'Specialty'})
    
    # build `line` - note that line_ds is repeated twice, because this column is not 
    # available in the SAP database
    contract['line'] = all4hierarchy(
        ds=contract.line_ds, lc=contract.mrl_lc, air=contract.crm_id_mrl, sap=contract.line_ds)

    # delete all four input columns if `delete_once_renamed` is True
    if delete_once_renamed:
        contract = contract.drop(columns='line_ds mrl_lc crm_id_mrl'.split())

    # contract name
    contract['contract_name'] = all4hierarchy(
        ds=contract.contract_name_ds, lc=contract.account_desc_lc, air=contract.contract_name_ds, sap=contract.contract_name_ds)

    # delete all four input columns if `delete_once_renamed` is True
    if delete_once_renamed:
        contract = contract.drop(columns='contract_name_ds account_desc_lc'.split())

    # some recoding on the contract name:
    # 1. if the contract name is 0, then replace with 'temp'
    # 2. if the contract name is blank, then replace with 'temp'
    # 3. if the contract name is ' ', then replace with 'temp'
    # the contracts whose names are set to 'temp' will be given a name later
    contract['contract_name'] = (contract['contract_name']
                                 .mask(contract['contract_name'].eq(0), other='temp')
                                 .mask(contract['contract_name'].eq(''), other='temp')
                                 .mask(contract['contract_name'].eq(' '), other='temp')
                                 )

    # program
    # this next line is a bit complicated, but what it does is:
    # 1. if the contract_type_ds is NOT 0, then replace with the program_lc
    # 2. if the contract_type_ds is NOT '0', then replace with the program_lc

    contract['contract_type_ds'] = contract['contract_type_ds'].where(contract['contract_type_ds'].ne(
        0), other=contract.program_lc).where(contract['contract_type_ds'].ne('0'), other=contract.program_lc)
    contract['program'] = all4hierarchy(ds=contract.contract_type_ds.where(contract.contract_type_ds.ne(
        0), other=contract.program_lc), lc=contract.program_lc, air=contract.program_air, sap=contract.contract_type_ds)
    contract['program'] = contract.program.mask(contract.program.eq('0'), other='').mask(
        contract.program.eq(''), other='').mask(contract.program.eq(' '), other='')

    # WC Catastrophe Excess of Loss
    # 'Per Occurrence Cat XOL'
    # This is to recode one specific program name
    contract['program'] = (contract.program
                           # missing WC Cat XOL is per occ cat xol
                           .mask(
                                # if program is 0 or blank and contract name is WC Cat XOL
                                np.logical_and(
                                    np.logical_or(
                                        contract.program.eq(0), contract.program.eq('')
                                    )
                                    , contract.contract_name.eq('WC Catastrophe Excess of Loss')
                                )
                            # then program is Per Occ Cat XOL
                            , other='Per Occurrence Cat XOL'
                            )
                           )

    # here are a few additional programs that need to be recoded:
    # 1. if the program is 0, then replace with ''
    # 2. if the program is blank, then replace with ''
    # 3. if the program is ' ', then replace with ''

    # use the np.select function to recode the program column
    # this starts by defining conditions and choices
    cond = [
        # Condition 1: does the contract name contain 'Per Policy XOL' anywhere?
        contract.contract_name.str.contains("Per Policy XOL")
        
        # Condition 2: does the contract name contain 'WC Catastrophe Excess of Loss' anywhere?
        , contract.contract_name.str.contains("WC Catastrophe Excess of Loss")
        ]

    # if the program has either of these two substrings,
    # then replace with the corresponding choice general options
    choices = [
        # Choice 1: if the contract name contains 'Per Policy XOL',
        # then replace the entire program column with 'Per Policy XOL'
        'Per Policy XOL'
        
        # Choice 2: if the contract name contains 'WC Catastrophe Excess of Loss',
        # then replace the entire program column with 'Per Occurrence Cat XOL'
        , 'Per Occurrence Cat XOL'
        ]

    # now use the np.select function to recode the program column, but 
    # only if the program column is blank (this is why we did the recoding before)
    contract['program'] = (
        contract['program']
        .where(
            contract['program'].notna()
            , other=np.select(cond, choices, '')
        )
    )

    # trigger is one of three values: RA, LO, or LD, which stand for
    # "Risks Attaching", "Losses Occurring", and "Losses Discovered"
    # this section uses the all4hierarchy function to recode the trigger column
    # so that it is consistent
    contract['trigger_long'] = all4hierarchy(ds=contract.trigger_ds, lc=contract.treaty_basis_lc

        # this line defines that the trigger equals "Risks Attaching"
        # if the contract name is "Freddie Mac"
        , air=contract.trigger_ds.mask(
            contract.contract_name.eq('Freddie Mac'), other='Risks Attaching'
            )

            , sap=contract.trigger_ds)

    # recode the trigger column so that NA values are replaced with the treaty basis
    # from the loss cost DB
    contract['trigger_long'] = (
        contract['trigger_long']
        .where(
            contract['trigger_long'].notna()
            , other=contract.treaty_basis_lc
        )
    )

    # define a `trigger` column that is the same as the `trigger_long` column,
    # but with the values recoded to RA, LO, or LD
    contract['trigger'] = contract['trigger_long'].map(
        {'Risks Attaching': 'RA', 'Losses Occurring': 'LO', 'Losses Discovered': 'LD'}
    )

    # treaty category 
    contract['treaty_category'] = contract['treaty_category_ds'].mask(
        contract['treaty_category_ds'].isna(), other='Missing')

    # currency
    contract['currency'] = all4hierarchy(
        ds=contract.currency_ds, lc=contract.currency_lc, air=contract.currency_air, sap=contract.currency_ds)

    # create something if contract name is missing
    temp_name = (
        # start with the line, eff_date, and program columns
        contract['line program eff_date'.split()]
        
        # join them together with a space after converting the final column to
        # the year instead of the full date
        .apply(lambda x: '{} {} {}'.format(x[0], x[1], x[2].year), axis=1)
    )

    # replace missing contract names with the temp_name
    contract['contract_name'] = (
        contract.contract_name
        
        # use the `mask` function to replace contract names 'temp' with the
        # actual value defined as `temp_name`
        .mask(contract.contract_name.eq('temp'), other=temp_name)
        
        # use the `mask` function to replace contract names ' ' with the
        # actual value defined as `temp_name`
        .mask(contract.contract_name.eq(' '), other=temp_name)

        # otherwise, just use the contract name
    )


    # territory
    contract['territory'] = all4hierarchy(
        ds=contract.terr_ds, lc=contract.region_lc, air=contract.region_air, sap=contract.terr_ds)

    # replace missing values with 'Missing' so that they can be grouped together
    # or filtered out, etc
    contract['territory'] = contract['territory'].mask(
        contract['territory'].eq(0), other='Missing')

    # broker
    contract['broker'] = all4hierarchy(
        ds=contract.broker_ds, lc=contract.broker_air, air=contract.broker_ds, sap=contract.broker_ds)
    
    # replace missing values with 'Missing' so that they can be grouped together
    # or filtered out, etc
    contract['broker'] = contract['broker'].mask(
        contract['broker'].eq(0), other='Missing')

    # last updated date
    # replace missing values with 1/1/1900, so that they can be grouped together
    # or filtered out, etc
    contract['last_updated_lc'] = contract['last_updated_lc'].mask(
        contract['last_updated_lc'].isna(), other=datetime.datetime.fromisoformat('1990-01-01'))
    contract['last_updated_ds'] = contract['last_updated_ds'].mask(
        contract['last_updated_ds'].isna(), other=datetime.datetime.fromisoformat('1990-01-01'))
    contract['last_updated_air'] = contract['last_updated_air'].mask(
        contract['last_updated_air'].isna(), other=datetime.datetime.fromisoformat('1990-01-01'))

    # max of the 3 `last_updated` columns:
    # should work like this, but faster:
    # contract['last_updated'] = contract['last_updated_lc last_updated_ds last_updated_air'.split(
    # )].apply(lambda x: max(x[0], x[1], x[2]), axis=1)

    # first try to use the loss cost last updated date,
    # then the DS last updated date, then the AIR last updated date
    contract['last_updated'] = contract['last_updated_lc'].mask(
        contract['last_updated_lc'] > contract['last_updated_ds'], other=contract['last_updated_ds'])
    contract['last_updated'] = contract['last_updated'].mask(
        contract['last_updated'] > contract['last_updated_air'], other=contract['last_updated_air'])


    # drop out all ceded_retro contracts
    contract = contract.copy().query('treaty_category_ds != "Ceded Retrocession"')

    # return sorted contract table with only the columns we want
    contract = contract[['timestamp',
                         'crm_gp_id', 'crm_id', 'eff_date', 'exp_date',

                         'client_name',
                         # 'client_name_ds', 'client_name_air', 'account_lc','reassured_ds',

                         'line',
                         # 'mrl_lc','line_ds','crm_id_mrl',
                         'subline_ds',

                         'contract_name',
                         # 'account_desc_lc','contract_name_ds',

                         'program',
                         # 'contract_type_ds', 'program_lc','program_air',

                         'trigger', 'trigger_long',
                         # 'trigger_ds','treaty_basis_lc',

                         'alae_basis_lc',
                         'dominant_type_ds',

                         'treaty_category',
                         # 'treaty_category_ds',

                         # 'nature_of_treaty_sap',
                         # 'mga_ds',

                         'broker',
                         # 'broker_ds','broker_air',
                         # 'broker_numb_ds',

                         'cyber_agg_limit_ds', 'cyber_exposure_ds',
                         # 'uw_for_treaty_sap',
                         # 'acct_freq_numb_sap','acct_level_sap',

                         'territory',
                         # 'terr_ds','region_lc','region_air',
                         # 'exposure_terr_sap',
                         # 'business_type_numb_sap',
                         # 'cancel_date_sap','cancel_type_sap',
                         # 'peril_sap',
                         # 'loss_eval_date_lc',
                         'status_lc', 'status_ds', 'status_air',
                         # 'cat_model_version_lc',
                         'user_id_lc', 'user_name_air',

                         'last_updated',
                         'last_updated_ds', 'last_updated_lc', 'last_updated_air',

                         'currency',
                         # 'currency_ds','currency_lc','currency_air',

                         'source_file_ds', 'source_file_lc',
                         'share_point_file_ds', 'file_location_air',

                         # 'note_lc','note_ds','note_air',

                         'ult_cre_prem_ds', 'deposit_prem_ds',
                         'expected_loss_ds', 'model_expected_loss_ds',
                         'expense_ratio_ds',
                         'tech_uw_ratio_ds', 'uw_profit_ds', 'npv_uw_profit_ds', 'roe_change_ds',
                         'standalone_tvar_250_ds', 'standalone_roc_250_ds', 'diversified_tvar_250_ds', 'diversified_roc_250_ds', 'loss_cv_ds',
                         'chg_rate_adequacy_ds', 'rate_change_ds', 'program_rate_change_ds',
                         # 'company_id_ds','annual_values_ds','company_code_sap','end_of_acct_year_sap','specific_numb_retro_allowed_sap',
                         'executive_summary_air'
                         ]]

    contract.query('crm_id != "M0"', inplace=True)

    return (contract)

    ### NOW, after going through that entire process to clean the contract table,
    ### we can do almost the exact same thing to clean the layer terms table
    ### of course, we will not be able to reuse almost any of the code, but
    ### it's good to keep in mind that this is the same general process 


def cinre_lc_layers(lc_conn : pyodbc.Connection, earliest_eff_date : datetime.date = datetime.date.fromisoformat('2020-01-01')):
    """
    # Description:
        Read in the layer terms table from the loss cost DB
    # Parameters:
        lc_conn: pyodbc.Connection object
            connection to the loss cost DB
        earliest_eff_date: datetime.date object
            earliest effective date to include in the table
            Default: 2020-01-01
    # Returns:
        layer_lc: pandas.DataFrame
    """
    # print 
    print('reading layer terms table from loss cost DB')

    # read in table
    layer_lc = readtbl(['LayerTerms', lc_conn])

    # need contract table for filtering effective dates
    contract = cinre_lc_contract(lc_conn)


    # change column names
    layer_lc_curcols = ['CrmGroupID', 'CrmID', 'Layer', 'SubjectPremium', 'RiskLimit', 'RiskRetention', 'OccLimit', 'ReinstStrg', 'Aad', 'AggLimit', 'LossCorrStart', 'LossCorrStop', 'Brokerage', 'RpBrokerage', 'Rate', 'SwingMinRate', 'SwingMaxRate', 'SwingLoad', 'UlaeRatio', 'ProfitComm', 'MaxPc', 'ReinsExpLoad', 'Comm', 'SsLrMin', 'SsSlide1', 'SsLrMid', 'SsSlide2', 'SsLrMax', 'ReinsPremium100', 'NonCatAvgLossAlae', 'MdlCatAvgLossAlae', 'MdlHuEqCatAvgLossAlae', 'MdlAOCatAvgLossAlae', 'NmdCatAvgLossAlae', 'RawNonCatCV', 'NonCatParmRisk', 'NonCatCV', 'RawNmdCatCV',
                        'NmdCatParmRisk', 'NmdCatCV', 'InterestRate', 'Bound', 'AuthorizedShare', 'FotRate', 'QuoteRate', 'SignedShare', 'CreProPrem', 'CreDepPrem', 'CreUltPrem', 'CreCedComm', 'CreBrokExp', 'CreAoExp', 'CreUw', 'CreNpvUw', 'ClashType', 'ClashCoverage', 'CyberSublimit', 'TerrorCoverage', 'TerrorSublimit', 'CatCoverageType', 'CatExperienceLoad', 'CyberCoverage', 'Placement', 'EcoXpl', 'DJ', 'TrapValExpLim', 'MarginalTvar50', 'MarginalTvar250', 'LayerMinCapital', 'CurrencyByLayer', 'TotCasAggLim', 'PricingType', 'OccRet', 'GrNetAggRet', 'GrNetAggLim', 'Maol']
    layer_lc_newcols = ['crm_gp_id', 'crm_id', 'layer', 'subject_premium', 'risk_limit', 'risk_retention', 'occ_limit', 'reinstatement_string', 'aad', 'agg_limit', 'loss_corr_start', 'loss_corr_stop', 'brokerage', 'rp_brokerage', 'rate', 'swing_min_rate', 'swing_max_rate', 'swing_load', 'ulae_ratio', 'profit_comm', 'max_pc', 'reins_exp_load', 'comm', 'ss_lr_min', 'ss_slide1', 'ss_lr_mid', 'ss_slide2', 'ss_lr_max', 'reins_premium_100', 'non_cat_ave_loss_alae', 'mdl_cat_ave_loss_alae', 'mdl_hu_eq_cat_ave_loss_alae', 'mdl_ao_cat_ave_loss_alae', 'nmd_cat_ave_loss_alae', 'raw_non_cat_cv', 'non_cat_param_risk', 'non_cat_cv', 'raw_nmd_cat_cv',
                        'nmd_cat_param_risk', 'nmd_cat_cv', 'interest_rate', 'bound', 'authorized_share', 'fot_rate', 'quote_rate', 'signed_share', 'cre_pro_prem', 'cre_deposit_prem', 'cre_ult_prem', 'cre_ceded_comm', 'cre_brok_exp', 'cre_ao_exp', 'cre_uw', 'cre_npv_uw', 'clash_type', 'clash_coverage', 'cyber_sublimit', 'terror_coverage', 'terror_sublimit', 'cat_coverage_type', 'cat_experience_load', 'cyber_coverage', 'placement', 'eco_x_pl', 'dj', 'trap_val_exp_lim', 'marginal_tvar_50', 'marginal_tvar_250', 'layer_min_capital', 'currency_by_layer', 'tot_cas_agg_lim', 'pricing_type', 'occ_ret', 'gr_net_agg_ret', 'gr_net_agg_lim', 'maol']
    layer_lc.rename(columns=dict(
        zip(layer_lc_curcols, [c + '_lc' for c in layer_lc_newcols])), inplace=True)

    # inception dates 2020 & later
    layer_lc = layer_lc.loc[layer_lc['crm_id_lc'].isin(
        contract.crm_id_lc.drop_duplicates().tolist()), :].reset_index(drop=True)

    # recode character cols to categories
    # for col in ['crm_id_lc','reinstatement_string_lc','clash_type_lc','clash_coverage_lc','terror_coverage_lc','cat_coverage_type_lc','cyber_coverage_lc','eco_x_pl_lc','dj_lc','currency_by_layer_lc','pricing_type_lc','gr_net_agg_ret_lc','gr_net_agg_lim_lc']:
    # layer_lc[col] = layer_lc[col].astype('category')

    # recode layer_lc so can join
    layer_lc['layer_lc'] = layer_lc['layer_lc'].astype('float')

    # GET EFF DATE FOR JOIN
    layer_lc = layer_lc.merge(contract['crm_gp_id_lc crm_id_lc eff_date_lc exp_date_lc'.split(
    )], how='left', on='crm_gp_id_lc crm_id_lc'.split())

    # return table
    return (layer_lc)


def cinre_ds_layers(ds_conn):
    print('reading layer table from deal sheet DB')
    # read in table
    layer_ds = readtbl(['Layer', ds_conn])

    # get contract table as well with a few key columns
    contract = cinre_dealsheet_contract(ds_conn)[
        'crm_gp_id_ds crm_id_ds eff_date_ds exp_date_ds expense_ratio_ds tech_uw_ratio_ds ult_cre_prem_ds'.split()].drop_duplicates()
    contract.rename(columns=dict(expense_ratio_ds='expense_ratio_ds_contract',
                    tech_uw_ratio_ds='tech_uw_ratio_ds_contract', ult_cre_prem_ds='ult_cre_prem_ds_contract'), inplace=True)

    # add timestamp
    # layer_ds['timestamp_ds'] = build_timestamp()

    # recode datetime columns
    for c in 'Inception Expiration'.split():
        layer_ds[c] = pd.to_datetime(layer_ds[c])

    # change column names
    layer_ds_curcols = ['CinReId', 'LayerID', 'LayerName', 'NewRenew', 'Inception', 'Expiration', 'SAPTreaty', 'SAPSection', 'ContractType', 'DominantType', 'Territory', 'UWArea', 'Limit', 'Retention', 'Reinstatements', 'MaxPolicyLimit', 'AggLimit', 'AggRetention', 'Currency', 'Trigger', 'ReportRemit', 'ALAE', 'Placement', 'Rate', 'ROL', 'AuthorizedLine',
                        'SignedLine', 'UltCinRePrem', 'ExpectedLoss', 'TechUWRatio', 'UWProfit', 'NPVUWProfit', 'TVaR250', 'ROE250', 'RateChange', 'DepositPrem', 'CyberExposure', 'CyberAggLimit', 'CatDBLayerID', 'Note', 'MinimumPrem', 'DepPremSchedule', 'LossCostDBLayerID', 'PNOC', 'OrgInception', 'OrgExpiration', 'SubjectPrem', 'SubjectBase', 'Brokerage', 'RPBrokerage']
    layer_ds_newcols = ['crm_gp_id', 'layer_id', 'layer_name', 'new_renew', 'eff_date', 'exp_date', 'sap_treaty', 'sap_section', 'contract_type', 'dominant_type', 'terr', 'uw_area', 'limit', 'retention', 'reinstatements', 'max_policy_limit', 'agg_limit', 'agg_retention', 'currency', 'trigger', 'report_remit', 'alae', 'placement', 'rate', 'rol', 'authorized_line',
                        'signed_line', 'ult_cre_prem', 'expected_loss', 'tech_uw_ratio', 'uw_profit', 'npv_uw_profit', 'tvar_250', 'roe_250', 'rate_change', 'deposit_prem', 'cyber_exposure', 'cyber_agg_limit', 'cat_db_layer_id', 'note', 'min_prem', 'dep_prem_schedule', 'cinre_lc_layer_id', 'pnoc', 'org_eff_date', 'org_exp_date', 'subject_prem', 'subject_base', 'brokerage', 'rp_brokerage']
    layer_ds.rename(columns=dict(
        zip(layer_ds_curcols, [c + '_ds' for c in layer_ds_newcols])), inplace=True)

    # inception dates 2020 & later
    layer_ds = layer_ds.loc[layer_ds['eff_date_ds'] >= datetime.datetime.fromisoformat(
        '2020-01-01'), :].reset_index(drop=True)

    # join in contract columns
    layer_ds = layer_ds.merge(
        contract, how='left', on='crm_gp_id_ds eff_date_ds exp_date_ds exp_date_ds'.split())

    # sort by crm_gp_id
    layer_ds = layer_ds.sort_values(
        'crm_gp_id_ds layer_name_ds'.split()).reset_index(drop=True)

    # return table
    return (layer_ds)


def cinre_air_layers(air_conn):
    print('reading layer table from AIR DB')
    # old/new column names
    old_layer_cols = ['CRMID', 'CinReID', 'Name', 'Program', 'Inception', 'Expiration', 'Status', 'Broker', 'Region', 'Currency', 'LayerType', 'Rol', 'OccLimit', 'OccRetention', 'Franchise', 'ReinstatementNumber', 'ReinstatementRate', 'ReinstatementStr',
                      'AggLimit', 'AggRetention', 'Participation', 'Components', 'SharesPriced', 'SharesAuthorized', 'SharesSigned', 'Brokerage', 'RpBrokerage', 'LayerId', 'RppRefRol', 'Comments', 'PricingRegistry', 'CinReGroupID', 'Lc_AppliesAgg', 'Lc_RatioToAgg']
    new_layer_cols = ['crm_id', 'cre_id', 'name', 'program', 'eff_date', 'exp_date', 'status', 'broker', 'region', 'currency', 'layer_type', 'rol', 'occ_limit', 'occ_retention', 'franchise', 'reinstatement_numb', 'reinstatement_rate', 'reinstatement_str',
                      'agg_limit', 'agg_retention', 'participation', 'components', 'shares_priced', 'shares_authorized', 'shares_signed', 'brokerage', 'rp_brokerage', 'layer_id', 'rpp_ref_rol', 'comments', 'pricing_registry', 'cre_gp_id', 'lc_applies_agg', 'lc_ratio_to_agg']

    # read table
    raw_layer_air = readtbl(['PricingLayerTermsv8-vw', air_conn])

    # rename columns
    raw_layer_air.rename(columns=dict(
        zip(old_layer_cols, [c+'_air' for c in new_layer_cols])), inplace=True)

    # recode dates to datetime
    for c in 'eff_date_air exp_date_air'.split():
        raw_layer_air[c] = pd.to_datetime(raw_layer_air[c])

    # eff_date >= 1/1/2020
    raw_layer_air = raw_layer_air.loc[raw_layer_air.eff_date_air >=
                                      datetime.datetime.fromisoformat('2020-01-01'), :]

    # ensure contracts in line with contracts_air table
    contract_air = cinre_air_contract(air_conn)
    air_crmids = contract_air['crm_id_air crm_gp_id_air eff_date_air'.split(
    )].drop_duplicates()

    # merge the two tables
    layer_air = raw_layer_air.merge(
        air_crmids, how='outer', on='crm_id_air eff_date_air'.split())

    # return the table
    return (layer_air)


def raw_layers(lc_conn, ds_conn, sap_conn, air_conn):
    # build indiviual tables
    layer_lc = cinre_lc_layers(lc_conn)
    layer_ds = cinre_ds_layers(ds_conn)
    layer_air = cinre_air_layers(air_conn)

    print("joining layer tables")
    # merge together
    layer = (layer_lc
             .merge(layer_ds, how='outer', left_on='crm_gp_id_lc layer_lc eff_date_lc'.split(), right_on='crm_gp_id_ds layer_id_ds eff_date_ds'.split())
             .merge(layer_air, how='outer', left_on='crm_gp_id_ds cinre_lc_layer_id_ds eff_date_ds'.split(), right_on='crm_gp_id_air layer_id_air eff_date_air'.split())
             )

    print('updating layer table columns')
    # add timestamp
    layer['timestamp'] = build_timestamp()

    # crm_gp_id
    layer['crm_gp_id'] = all4hierarchy(
        ds=layer.crm_gp_id_ds, lc=layer.crm_gp_id_lc, air=layer.crm_gp_id_air, sap=layer.crm_gp_id_ds)

    # crm_id
    layer['crm_id'] = all4hierarchy(
        ds=layer.crm_id_ds, lc=layer.crm_id_lc, air=layer.crm_id_air, sap=layer.crm_id_ds)

    # layer_id
    layer['layer_id'] = all4hierarchy(
        ds=layer.layer_id_ds, lc=layer.cinre_lc_layer_id_ds, air=layer.layer_lc, sap=layer.layer_id_air)

    # eff_date
    layer['eff_date'] = all4hierarchy(
        ds=layer.eff_date_ds, lc=layer.eff_date_lc, air=layer.eff_date_air, sap=layer.eff_date_ds)

    # exp_date
    layer['exp_date'] = all4hierarchy(
        ds=layer.exp_date_ds, lc=layer.exp_date_lc, air=layer.exp_date_air, sap=layer.exp_date_ds)

    # make date cols datetime
    for c in 'eff_date exp_date'.split():
        layer[c] = pd.to_datetime(layer[c])

    # occ_limit
    layer['occ_limit'] = all4hierarchy(
        ds=layer.occ_limit_lc, lc=layer.occ_limit_air, air=layer.occ_limit_lc, sap=layer.occ_limit_lc)

    # occ_retention
    layer['occ_retention'] = all4hierarchy(
        ds=layer.occ_ret_lc, lc=layer.occ_retention_air, air=layer.occ_ret_lc, sap=layer.occ_ret_lc)

    # risk limit
    layer['risk_limit'] = all4hierarchy(
        ds=layer.limit_ds, lc=layer.risk_limit_lc, air=layer.limit_ds, sap=layer.limit_ds)
    layer['risk_limit'] = layer['risk_limit'].mask(
        layer['risk_limit'].eq(0), other=layer['risk_limit_lc'])

    # agg limit
    layer['agg_limit'] = all4hierarchy(
        ds=layer.agg_limit_ds, lc=layer.agg_limit_lc, air=layer.agg_limit_air, sap=layer.agg_limit_ds)

    # agg retention
    layer['agg_retention'] = all4hierarchy(
        ds=layer.agg_retention_ds, lc=layer.aad_lc, air=layer.agg_retention_air, sap=layer.agg_retention_ds)

    # risk retention
    layer['risk_retention'] = all4hierarchy(
        ds=layer.retention_ds, lc=layer.risk_retention_lc, air=layer.retention_ds, sap=layer.retention_ds)

    # brokerage
    layer['brokerage'] = all4hierarchy(
        ds=layer.brokerage_ds, lc=layer.brokerage_lc, air=layer.brokerage_air, sap=layer.brokerage_ds)

    # rp brokerage
    layer['rp_brokerage'] = all4hierarchy(
        ds=layer.rp_brokerage_ds, lc=layer.rp_brokerage_lc, air=layer.rp_brokerage_air, sap=layer.rp_brokerage_ds)

    # reinstatement_string
    layer['reinstatement_string'] = all4hierarchy(
        ds=layer.reinstatements_ds, lc=layer.reinstatement_string_lc, air=layer.reinstatement_str_air, sap=layer.reinstatements_ds)

    # subject prem
    layer['subject_prem'] = all4hierarchy(
        ds=layer.subject_prem_ds, lc=layer.subject_premium_lc, air=layer.subject_prem_ds, sap=layer.subject_prem_ds)

    # deposit_prem
    layer['deposit_prem'] = all4hierarchy(
        ds=layer.deposit_prem_ds, lc=layer.cre_deposit_prem_lc, air=layer.deposit_prem_ds, sap=layer.deposit_prem_ds)

    # ultimate_prem
    layer['ultimate_prem'] = all4hierarchy(
        ds=layer.ult_cre_prem_ds, lc=layer.cre_ult_prem_lc, air=layer.ult_cre_prem_ds, sap=layer.ult_cre_prem_ds)

    # ult prem for contract
    prem = layer['crm_id eff_date ultimate_prem'.split()].groupby('crm_id eff_date'.split(
    ), observed=False).sum().reset_index().rename(columns=dict(ultimate_prem='ultimate_prem_contract'))
    layer = layer.merge(prem, how='left', on='crm_id eff_date'.split())

    # uw profit
    layer['uw_profit'] = all4hierarchy(
        ds=layer.uw_profit_ds, lc=layer.cre_uw_lc, air=layer.uw_profit_ds, sap=layer.uw_profit_ds)

    # npv uw profit
    layer['npv_uw_profit'] = all4hierarchy(
        ds=layer.npv_uw_profit_ds, lc=layer.cre_npv_uw_lc, air=layer.npv_uw_profit_ds, sap=layer.npv_uw_profit_ds)

    # authorized share
    layer['authorized_share'] = all4hierarchy(
        ds=layer.authorized_line_ds, lc=layer.authorized_share_lc, air=layer.shares_authorized_air, sap=layer.authorized_line_ds)

    # signed share
    layer['signed_share'] = all4hierarchy(
        ds=layer.signed_line_ds, lc=layer.signed_share_lc, air=layer.shares_signed_air, sap=layer.signed_line_ds)

    # rate
    layer['rate'] = all4hierarchy(
        ds=layer.rate_ds, lc=layer.rate_lc, air=layer.rate_ds, sap=layer.rate_ds)

    # rol
    layer['rol'] = all4hierarchy(
        ds=layer.rol_ds, lc=layer.rol_air, air=layer.rol_ds, sap=layer.rol_ds)

    # placement
    layer['placement'] = all4hierarchy(
        ds=layer.placement_ds, lc=layer.placement_lc, air=layer.placement_ds, sap=layer.placement_ds)

    # expected loss
    layer['calc_exp_loss'] = layer.non_cat_ave_loss_alae_lc + \
        layer.mdl_cat_ave_loss_alae_lc + layer.nmd_cat_ave_loss_alae_lc
    layer['expected_loss'] = all4hierarchy(
        ds=layer.expected_loss_ds, lc=layer.calc_exp_loss, air=layer.expected_loss_ds, sap=layer.expected_loss_ds)

    # expected loss for contract
    prem = layer['crm_id eff_date expected_loss'.split()].groupby('crm_id eff_date'.split(
    ), observed=False).sum().reset_index().rename(columns=dict(expected_loss='expected_loss_contract'))
    layer = layer.merge(prem, how='left', on='crm_id eff_date'.split())

    # pricing lr
    layer['expected_loss_ratio'] = layer.expected_loss / layer.ultimate_prem
    layer['expected_loss_ratio_contract'] = layer.expected_loss_contract / \
        layer.ultimate_prem_contract

    # calc expense
    layer['calc_expense'] = layer.ultimate_prem - \
        layer.expected_loss - layer.uw_profit
    layer['calc_expense_ratio1'] = layer.calc_expense / \
        layer.ultimate_prem - layer.profit_comm_lc
    layer['calc_expense_ratio2'] = layer.brokerage + layer.comm_lc

    layer['expense_ratio'] = layer.calc_expense_ratio2.where(
        layer.calc_expense_ratio2.ne(0), other=layer.calc_expense_ratio1)

    # broker dollars
    layer['broker_dollars'] = layer.ultimate_prem * layer.brokerage

    # cyber limit
    layer['cyber_limit'] = all4hierarchy(
        ds=layer.cyber_agg_limit_ds, lc=layer.cyber_sublimit_lc, air=layer.cyber_agg_limit_ds, sap=layer.cyber_agg_limit_ds)

    layer['cre_ao_ratio'] = (
        layer.cre_ao_exp_lc / layer.ultimate_prem).where(layer.ultimate_prem.ne(0), other=0)

    # cyber exposure
    layer['cyber_coverage'] = layer.cyber_exposure_ds.mask(
        layer.cyber_exposure_ds.isna(), other=layer.cyber_coverage_lc)

    # sort table columns
    col_ord = ['timestamp',
               'crm_gp_id', 'crm_id', 'layer_id', 'layer_name_ds',

               'eff_date', 'exp_date',
               'sap_treaty_ds', 'sap_section_ds',

               # 'max_policy_limit_ds',

               'risk_retention',
               # 'retention_ds','risk_retention_lc',

               'risk_limit',
               # 'limit_ds','risk_limit_lc',

               'occ_retention',
               # 'occ_ret_lc','occ_retention_air',

               'occ_limit',
               # 'occ_limit_lc', 'occ_limit_air',

               'agg_retention',
               # 'aad_lc','agg_retention_ds', 'agg_retention_air',

               'agg_limit',
               # 'agg_limit_lc', 'agg_limit_ds', 'agg_limit_air',
               # 'quote_rate_lc',

               'rate',
               # 'rate_lc', 'rate_ds',
               # 'fot_rate_lc',
               # 'rate_change_ds',

               'rol',
               # 'rol_ds', 'rol_air',

               'reinstatement_string',
               # 'reinstatements_ds', 'reinstatement_numb_air','reinstatement_rate_air',
               # 'reinstatement_string_lc', 'reinstatement_str_air',
               # 'rp_brokerage',
               # 'rp_brokerage_lc', 'rp_brokerage_ds', 'rp_brokerage_air',
               # 'alae_ds',
               # 'max_pc_lc',
               # 'reins_exp_load_lc',
               # 'reins_premium_100_lc',
               # 'dep_prem_schedule_ds',

               'subject_prem',
               # 'subject_premium_lc','subject_prem_ds',
               # 'subject_base_ds',
               # 'min_prem_ds',
               # 'cre_pro_prem_lc',

               'deposit_prem',
               # 'cre_deposit_prem_lc','deposit_prem_ds',
               # 'broker_dollars',

               'ultimate_prem',
               'ultimate_prem_contract',
               # 'ult_cre_prem_ds_contract',
               # 'cre_ult_prem_lc', 'ult_cre_prem_ds',

               'tech_uw_ratio_ds',
               # 'tech_uw_ratio_ds_contract',

               'brokerage',
               # 'brokerage_lc','brokerage_ds','brokerage_air','cre_brok_exp_lc',

               'comm_lc',
               # 'cre_ceded_comm_lc',

               'cre_ao_ratio', 'profit_comm_lc',

               'ulae_ratio_lc',

               # 'expense_ratio_ds_contract',
               # 'calc_expense_ratio','calc_expense',
               'expense_ratio',
               'expected_loss_ratio', 'expected_loss_ratio_contract',
               # 'expected_loss','expected_loss_contract',
               # 'expected_loss_ds', 'calc_exp_loss',
               # 'non_cat_ave_loss_alae_lc','mdl_cat_ave_loss_alae_lc','nmd_cat_ave_loss_alae_lc',
               # 'mdl_hu_eq_cat_ave_loss_alae_lc',
               # 'mdl_ao_cat_ave_loss_alae_lc',

               # 'cre_ao_exp_lc',

               'uw_profit',
               # 'cre_uw_lc','uw_profit_ds',

               'npv_uw_profit',
               # 'cre_npv_uw_lc','npv_uw_profit_ds',

               'clash_type_lc', 'clash_coverage_lc',

               'cyber_limit',
               # 'cyber_sublimit_lc', 'cyber_agg_limit_ds',

               'cyber_coverage',
               # 'cyber_coverage_lc', 'cyber_exposure_ds',

               'terror_coverage_lc', 'terror_sublimit_lc',

               'cat_coverage_type_lc', 'cat_experience_load_lc',

               'placement',
               # 'placement_lc', 'placement_ds',
               'eco_x_pl_lc',
               'dj_lc',
               'trap_val_exp_lim_lc',

               # 'roe_250_ds',
               # 'marginal_tvar_50_lc',
               # 'marginal_tvar_250_lc',
               # 'tvar_250_ds',

               # 'layer_min_capital_lc',

               'tot_cas_agg_lim_lc',
               'pricing_type_lc',

               'gr_net_agg_ret_lc', 'gr_net_agg_lim_lc',

               'maol_lc',

               # 'shares_priced_air',

               'authorized_share',
               # 'authorized_share_lc','authorized_line_ds','shares_authorized_air',

               'signed_share',
               # 'signed_share_lc','signed_line_ds','shares_signed_air',

               'pnoc_ds',

               'franchise_air',

               'ss_lr_min_lc', 'ss_slide1_lc', 'ss_lr_mid_lc', 'ss_slide2_lc', 'ss_lr_max_lc',

               'loss_corr_start_lc', 'loss_corr_stop_lc',

               'swing_min_rate_lc', 'swing_max_rate_lc', 'swing_load_lc',

               'raw_non_cat_cv_lc', 'non_cat_param_risk_lc', 'non_cat_cv_lc', 'raw_nmd_cat_cv_lc', 'nmd_cat_param_risk_lc', 'nmd_cat_cv_lc',

               'participation_air',
               # 'components_air',

               'rpp_ref_rol_air',

               'pricing_registry_air',
               'lc_applies_agg_air',
               'lc_ratio_to_agg_air'
               ]

    layer = layer[col_ord]
    layer.rename(columns=dict(zip(layer.columns.tolist(), [
                 c + '_layer' for c in layer.columns.tolist()])), inplace=True)
    layer.rename(columns=dict(zip('crm_gp_id_layer crm_id_layer eff_date_layer exp_date_layer layer_id_layer'.split(
    ), 'crm_gp_id crm_id eff_date exp_date layer_id'.split())), inplace=True)

    # add in the number of layers for each contract
    layer = layer.merge(
        (layer['crm_gp_id crm_id eff_date exp_date layer_id'.split()]
         .drop_duplicates()
         .groupby('crm_gp_id crm_id eff_date exp_date'.split(), observed=False)
         .count()
         .reset_index()
         .rename(columns=dict(layer_id='layer_count'))
         ), how='left', on='crm_gp_id crm_id eff_date exp_date'.split()
    )

    # if layer name is missing, add it in
    layer['layer_name_default'] = layer.layer_id.apply(
        lambda x: 'Layer 1' if np.isnan(x) else 'Layer ' + str(int(x)))
    layer['layer_name_missing'] = ""
    layer['layer_name_exists'] = layer.layer_count.gt(1)
    layer['layer_ds_name_exists'] = layer.layer_name_ds_layer.notna()
    layer['layer_name'] = layer.layer_name_ds_layer.where(layer.layer_name_ds_layer.notna(
    ), other=layer.layer_name_default.where(layer.layer_name_exists, other=layer.layer_name_missing))
    # layer.drop('layer_name_default layer_name_missing layer_name_exists layer_ds_name_exists'.split(), 1, inplace=True)

    # remove essent
    layer = layer.query("layer_name_ds_layer!='Essent'")

    # return total layer table
    return (layer)


def read_sap_tbl(ds_conn):
    print('reading SAP lookup')
    sap_tbl = readtbl(['CRMIDforSAP', ds_conn])
    sap_tbl.rename(columns=dict(zip(sap_tbl.columns.tolist(
    ), 'cre_id crm_id eff_date exp_date treaty_category sap_treaty sap_section line'.split())), inplace=True)
    sap_tbl['crm_gp_id'] = sap_tbl['crm_id'].apply(lambda x: int(x[1:]))
    sap_tbl.drop('cre_id', 1, inplace=True)

    for c in 'eff_date exp_date'.split():
        sap_tbl[c] = pd.to_datetime(sap_tbl[c])

    sap_tbl.rename(columns=dict(zip(sap_tbl.columns.tolist(), [
                   c + '_crmidforsap' for c in sap_tbl.columns.tolist()])), inplace=True)
    return (sap_tbl)


def join_layer_contract1(lc_conn, ds_conn, sap_conn, air_conn):
    raw_contract = raw_contracts(lc_conn, ds_conn, sap_conn, air_conn)
    raw_layer = raw_layers(lc_conn, ds_conn, sap_conn, air_conn)

    print('joining the contract table to the layer table')
    out = raw_layer.merge(raw_contract, how='left',
                          on='crm_gp_id crm_id eff_date exp_date'.split())

    # contract term
    out['contract_term'] = out['eff_date exp_date'.split()].apply(lambda x: (
        12*x[1].year + x[1].month) - (12*x[0].year + x[0].month) + 1, axis=1)

    # use program to assign to reserving analysis line
    xol_program_list = ['Aggregate XOL', 'Per Claim XOL', 'Per Occurence XOL', 'Per Occurrence Cat XOL',
                        'Per Occurrence XOL', 'Per Policy XOL', 'Per Risk XOL', 'Risk Aggregate XOL']
    qs_program_list = ['Cat Quota Share',
                       'Pro Rata/Quota Share', 'Pro-Rata/Quota Share ']
    var_qs_program_list = ['Variable Quota Share']
    cat_program_list = ['Cat Quota Share', 'Per Occurrence Cat XOL', 'Aggregate CAT XOL - Occurrence Exposed',
                        'Aggregate Cat XOL', 'MY Per Occurrence Cat XOL', 'Per Occurrence Cat XOL Multiyear', 'Per Occurrence Cat XOL Annual']
    ppr_program_list = ['Risk Aggregate XOL', 'Per Risk XOL']
    agg_xol_program_list = ['Aggregate XOL', 'Risk Aggregate XOL',
                            'Aggregate CAT XOL - Occurrence Exposed', 'Aggregate Cat XOL', 'Aggregate XOL (Occurrence Exposed)']
    surplus_share_program_list = ['Surplus Share']

    out['one'], out['zero'] = 1, 0

    # xol_ind
    out['xol_ind'] = out.one.where(
        out.program.isin(xol_program_list), other=out.zero)

    # qs_ind
    out['qs_ind'] = out.one.where(out.program.isin(
        qs_program_list), other=out.zero).mask(out.placement_layer.lt(1), other=1)

    # cat_ind
    out['cat_ind'] = out.one.where(
        out.program.isin(cat_program_list), other=out.zero)

    # ppr_ind
    out['ppr_ind'] = out.one.where(out.program.isin(
        ppr_program_list), other=out.zero).where(out.line.eq('Property'), other=out.zero)

    # agg xol ind
    out['agg_xol_ind'] = out.one.where(
        out.program.isin(agg_xol_program_list), other=out.zero)

    # surplus share ind
    out['surplus_share_ind'] = out.one.where(
        out.program.isin(surplus_share_program_list), other=out.zero)

    # variable qs ind
    out['var_qs_ind'] = out.one.where(
        out.program.isin(var_qs_program_list), other=out.zero)

    # transactional ind
    out['trans_ind'] = out.one.where(
        out.contract_name.str.lower().str.find('transaction').ne(-1), other=out.zero)
    # out['trans_ind'] = out.contract_name.apply(lambda x: 0 if x.lower().find('transactional') == -1 else 1)

    # clash ind
    out['clash_ind'] = out.one.where(np.logical_and(out.line.eq(
        'Casualty'), out.program.str.lower().eq('clash')), other=out.zero)

    # assign reserving line
    cond = [
        # casualty np
        np.logical_and(out.line.eq('Casualty'), np.logical_and(out.xol_ind.eq(1), np.logical_and(
            out.cat_ind.eq(0), np.logical_and(out.qs_ind.eq(0), out.trans_ind.eq(0))))),

        # casualty pr
        np.logical_and(out.line.eq('Casualty'), np.logical_and(
            out.qs_ind.eq(1), out.trans_ind.eq(0))),

        # ppr
        np.logical_and(out.line.eq('Property'), out.ppr_ind.eq(1)),

        # property cat
        np.logical_and(out.line.eq('Property'), out.cat_ind.eq(1)),

        # cirt
        np.logical_and(out.line.eq('Specialty'), out.contract_term.ge(90)),

        # other specialty
        np.logical_and(out.line.eq('Specialty'), out.contract_term.lt(90)),

        # transactional
        np.logical_and(out.line.eq('Casualty'), np.logical_and(
            out.trans_ind.eq(1), out.contract_name.notna())),

        # other property cat
        np.logical_and(out.line.eq('Property'), np.logical_and(
            out.ppr_ind.eq(0), out.cat_ind.eq(1))),

        # other property non cat
        np.logical_and(out.line.eq('Property'), np.logical_and(
            out.ppr_ind.eq(0), out.cat_ind.eq(0))),

        # WC cat
        np.logical_and(out.line.eq('Casualty'), out.cat_ind.eq(1)),

        # clash
        out.clash_ind.eq(1)
    ]

    choices = [
        'casualty_np',
        'casualty_pr',
        'property_per_risk',
        'property_cat',
        'cirt',
        'specialty',
        'transactional',
        'other_property_cat',
        'other_property_noncat',
        'wc_cat',
        'clash'
    ]

    # set up reserving line field
    out['reserving_line'] = np.select(cond, choices, 'other')

    # read sap table
    sap_tbl = read_sap_tbl(ds_conn)

    # join sap table
    out = out.merge(sap_tbl.drop('treaty_category_crmidforsap crm_gp_id_crmidforsap'.split(), 1), how='left', left_on='crm_id eff_date exp_date layer_id line'.split(
    ), right_on='crm_id_crmidforsap eff_date_crmidforsap exp_date_crmidforsap sap_section_crmidforsap line_crmidforsap'.split())

    # recode sap treaty
    out['sap_treaty'] = all4hierarchy(ds=out.sap_treaty_ds_layer, lc=out.sap_treaty_crmidforsap,
                                      air=out.sap_treaty_ds_layer, sap=out.sap_treaty_ds_layer)
    out['sap_section'] = all4hierarchy(
        ds=out.layer_id, lc=out.sap_section_crmidforsap, air=out.layer_id, sap=out.layer_id)

    # qs on deal ind
    qs_df = out['crm_id eff_date qs_ind'.split()].groupby(
        'crm_id eff_date'.split(), observed=False).sum().reset_index()
    qs_df['one'], qs_df['zero'] = 1, 0
    qs_df['qs_on_deal_ind'] = qs_df.one.where(
        qs_df.qs_ind.ge(1), other=qs_df.zero)

    # join qs_on_deal_ind
    out = out.merge(qs_df.drop('one zero qs_ind'.split(), 1),
                    how='left', on='crm_id eff_date'.split())

    # out.drop('one zero'.split(), 1, inplace=True)
    return (out)


def join_layer_contract(lc_conn, ds_conn, sap_conn, air_conn):
    df = join_layer_contract1(lc_conn, ds_conn, sap_conn, air_conn)

    # treaty year
    df['treaty_year'] = df.eff_date.dt.year

    # descr type
    cond = [
        df.xol_ind.eq(1),
        df.agg_xol_ind.eq(1),
        df.surplus_share_ind.eq(1),
        df.qs_ind.eq(1),
        df.var_qs_ind.eq(1)
    ]
    choices = [
        'XOL',
        'AGG XOL',
        'Surplus Share',
        'Quota Share',
        'Variable QS'
    ]
    df['descr_type'] = np.select(cond, choices, 'other')

    # qs on same deal?
    cond, choices = [df.qs_on_deal_ind.eq(1), df.qs_on_deal_ind.eq(0)], [
        'Yes', 'No']
    df['qs_on_deal'] = np.select(cond, choices)

    # multi layer always = "No"??
    df['multi_layer'] = 'No'

    # recode a few WC CAT treaties to the correct reserving line
    cond = [
        np.logical_and(df.reserving_line.eq('casualty_pr'), np.logical_and(
            df.line.eq('Casualty'), df.program.eq('Per Occurrence Cat XOL')))
    ]
    choices = [
        'wc_cat'
    ]
    df['reserving_line'] = np.select(cond, choices, df['reserving_line'])

    # recode missing crm_gp_id's
    df['crm_gp_id'] = df['crm_gp_id'].where(df['crm_gp_id'].ne(
        0), other=df.crm_id.str.lstrip(1).astype(float))
    df['crm_gp_id'] = df['crm_gp_id'].where(
        df['crm_gp_id'].notna(), other=0).astype(int)

    # better contract name & layer name
    df['contract_layer_name'] = df.client_name.str.strip().str.cat(
        others=df.contract_name.str.strip(), sep=' - ')
    df['contract_name2'] = df.contract_layer_name.str.cat(others=df.layer_name.str.strip(
    ).where(df.layer_name.str.strip().notna(), other=''), sep=' - ')

    # change contract_name
    df.rename(columns=dict(contract_name='old_contract_name'), inplace=True)

    # reorder columns
    col_ord = ['timestamp',
               'reserving_line',
               'crm_id',
               'sap_treaty',
               'sap_section',
               'contract_layer_name',
               'contract_name2',
               'eff_date',
               'treaty_year',
               'exp_date',
               'contract_term',
               'trigger',
               'descr_type',
               'expected_loss_ratio_layer',
               'expected_loss_ratio_contract_layer',
               'brokerage_layer',
               'comm_lc_layer',
               'expense_ratio_layer',
               'qs_on_deal',
               'ultimate_prem_layer',
               'ultimate_prem_contract_layer',
               'rate_layer',
               'signed_share_layer',
               'risk_limit_layer',
               'risk_retention_layer',

               'multi_layer',

               'reinstatement_string_layer',
               'agg_limit_layer',
               'agg_retention_layer',

               # assumed retrocession?

               'crm_gp_id',
               'trigger_long',

               'status_lc',
               'status_ds',
               'status_air',
               'source_file_ds',
               'share_point_file_ds',
               'source_file_lc',
               'file_location_air',

               'last_updated',
               'last_updated_ds',

               'occ_limit_layer',
               'occ_retention_layer',

               'rol_layer',
               'placement_layer',

               'line',
               'subline_ds',

               'program',
               'client_name',
               'old_contract_name',
               'layer_name',
               'layer_id',
               'layer_name_ds_layer',

               'subject_prem_layer',
               'deposit_prem_layer',

               'tech_uw_ratio_ds_layer',
               'uw_profit_layer',
               'npv_uw_profit_layer',
               'cre_ao_ratio_layer',
               'profit_comm_lc_layer',
               'ulae_ratio_lc_layer',

               'clash_type_lc_layer',
               'clash_coverage_lc_layer',
               'cyber_limit_layer',
               'cyber_coverage_layer',
               'cyber_agg_limit_ds',
               'cyber_exposure_ds',
               'terror_coverage_lc_layer',
               'terror_sublimit_lc_layer',
               'cat_coverage_type_lc_layer',
               'cat_experience_load_lc_layer',

               'territory',
               'currency',
               'treaty_category',

               'broker',

               'executive_summary_air',

               'last_updated_lc',
               'last_updated_air',
               'user_id_lc',
               'user_name_air',

               'eco_x_pl_lc_layer', 'dj_lc_layer',
               'trap_val_exp_lim_lc_layer',
               'tot_cas_agg_lim_lc_layer',
               'pricing_type_lc_layer',
               'gr_net_agg_ret_lc_layer',
               'gr_net_agg_lim_lc_layer',
               'maol_lc_layer',
               'authorized_share_layer',

               'pnoc_ds_layer',
               'franchise_air_layer',
               'ss_lr_min_lc_layer',
               'ss_slide1_lc_layer',
               'ss_lr_mid_lc_layer',
               'ss_slide2_lc_layer',
               'ss_lr_max_lc_layer',
               'loss_corr_start_lc_layer',
               'loss_corr_stop_lc_layer',
               'swing_min_rate_lc_layer',
               'swing_max_rate_lc_layer',
               'swing_load_lc_layer',

               'participation_air_layer',
               'rpp_ref_rol_air_layer',
               'pricing_registry_air_layer',
               'lc_applies_agg_air_layer',
               'lc_ratio_to_agg_air_layer',
               'layer_count',

               'alae_basis_lc',

               'roe_change_ds',
               'standalone_tvar_250_ds',
               'standalone_roc_250_ds',
               'diversified_tvar_250_ds',
               'diversified_roc_250_ds',
               'loss_cv_ds',
               'chg_rate_adequacy_ds',
               'rate_change_ds',
               'program_rate_change_ds',

               'dominant_type_ds',

               'xol_ind',
               'qs_ind',
               'cat_ind',
               'ppr_ind',
               'agg_xol_ind',
               'trans_ind',
               'clash_ind'
               ]

    # actual reorder step
    df = df[col_ord]

    # sort table
    df.sort_values(
        'eff_date reserving_line crm_id layer_id'.split(), inplace=True)

    # reset index
    df.reset_index(drop=True, inplace=True)

    # rename cols
    old_col = 'ultimate_prem_contract_layer rate_layer signed_share_layer contract_name2'.split()
    new_col = 'ultimate_prem_contract reinsurance_rate cre_participation contract_name'.split()
    df.rename(columns=dict(zip(old_col, new_col)), inplace=True)

    print('finished with data pull')

    return (df)
