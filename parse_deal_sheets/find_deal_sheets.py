import pandas as pd
import numpy as np
import pyxlsb
import os

from datetime import datetime, timedelta

import sys

# add the location of these scripts to the path so they can be imported
sys.path.append(r'O:\PARM\Corporate Actuarial\Reserving\Scripts\python')
sys.path.append('./')

# this is a script that contains functions to get user inputs
# this section is grabbing those inputs
import user_inputs as i
folder = i.get_folder()
show_every=i.get_show_every()

### given folder, return the subfolders
def get_subfolders(folder : str = None) -> list:
    """
    # Description
        Given a folder, return the subfolders
    # Inputs
        folder: string, the folder to search
    # Outputs
        out: list, the subfolders in the folder
    # Imports
        import os
    # Example
        >>> # assume there is a folder called "test" in the current directory
        >>> # with subfolders called "subtest1" and "subtest2"
        >>> get_subfolders(folder='test')
        ['subtest1', 'subtest2']
    """
    # get the list of files in the folder
    # `os.path.isdir(x)`` returns True if `x` is a directory
    # `os.listdir(folder)` returns a list of the files in the `folder`
    # uses list comprehension to create a list of booleans
    out = [os.path.isdir('{}\\{}'.format(folder, x)) for x in os.listdir(folder)]

    # use the list of booleans to filter the list of files
    # should reproduce this code, but as optimized as possible:
    # out2 = list(np.array(os.listdir(folder))[out])
    out2 = [x for x, y in zip(os.listdir(folder), out) if y]

    # this is better because:
    # 1. it doesn't require numpy
    # 2. it doesn't require a list comprehension (it uses a generator expression)

    # return the list of subfolders
    return(out2)
    
### given folder, find subfolders, then find their subfolders, until lowest level
def get_all_subfolders(folder : str = None) -> list:
    """
    # Description
        Given a folder, find subfolders, then find their subfolders, 
        and on and on, until reaching the lowest level
    # Inputs
        folder: string, the folder to search
    # Outputs
        out: list, the subfolders in the folder
    # Imports
        import os
    # Example
        >>> # assume there is a folder called "test" in the current directory
        >>> # with subfolders called "subtest1" and "subtest2"
        >>> # "subtest1" has subfolders called "subsubtest1" and "subsubtest2"
        >>> # "subtest2" has subfolders called "subsubtest3" and "subsubtest4"
        >>> get_all_subfolders(folder='test')
        ['subtest1', 'subtest2',
        'subtest1\\subsubtest1','subtest1\\subsubtest2',
        'subtest2\\subsubtest3', 'subtest2\\subsubtest4']
    """

    ## this function should reproduce the following, but as optimized for speed as possible
    # level = {}
    # level['1'] = ['{}\\{}'.format(folder, x) for x in get_subfolders(folder=folder)]
    # cur_level = 1
    # loop_ind = True
    # while loop_ind:
    #     prior_level = cur_level
    #     cur_level = cur_level + 1
        
    #     level['{}'.format(cur_level)] = []
    #     for fold in level['{}'.format(prior_level)]:
    #         level['{}'.format(cur_level)] = level['{}'.format(cur_level)] + ['{}\\{}'.format(fold, x) for x in get_subfolders(folder=fold)] 
            
    #     if len(level['{}'.format(cur_level)]) == len(level['{}'.format(prior_level)]):
    #         loop_ind = False
        
    # out = []
    # for k in list(level.keys()):
    #     out = out + level[k]

    level = {}

    # get the subfolders in the top level folder
    level['1'] = [os.path.join(folder, x) for x in get_subfolders(folder=folder)]

    # set the current level to 1
    cur_level = 1

    # set the loop indicator to True
    loop_ind = True

    # while the loop indicator is True
    while loop_ind:

        # set the prior level to the current level
        prior_level = cur_level

        # increment the current level
        cur_level = cur_level + 1

        # set the current level to an empty list
        level['{}'.format(cur_level)] = (x for x in level['{}'.format(cur_level)])

        # for each folder in the prior level
        for fold in level['{}'.format(prior_level)]:
                
                # get the subfolders in the folder
                level['{}'.format(cur_level)] = level['{}'.format(cur_level)] + (os.path.join(fold, x) for x in get_subfolders(folder=fold))

        # if the length of the current level is the same as the prior level
        if len(list(level['{}'.format(cur_level)])) == len(list(level['{}'.format(prior_level)])):
            
            # this means that there are no more subfolders, because otherwise the
            # length of the current level would be greater than the prior level
            # to break the loop, set the loop indicator to False
            loop_ind = False

    # initialize the output list
    out = []

    # for each key in the level dictionary (using a generator expression)
    for k in (x for x in level.keys()):
            
            # extend the output list with the list of folders in the current level
            out.extend(level[k])

    # return the output list
    return(out)
    
    
### given folder, retrun the files in that folder
def get_files(folder : str = None) -> list:
    """
    # Description
        Given a folder, return the files in that folder
    # Inputs
        folder: string, the folder to search
    # Outputs
        out2: list, the files in the folder
    # Imports
        import os
    # Example
        >>> # assume there is a folder called "test" in the current directory
        >>> # with files called "test1.txt" and "test2.txt"
        >>> get_files(folder='test')
        ['test1.txt', 'test2.txt']
    """
    # out = [os.path.isdir('{}\\{}'.format(folder, x)) for x in os.listdir(folder)] # this line can be optimized by using os.path.join instead of string concatenation:
    
    # this line can be optimized by using os.path.join instead of string concatenation
    # compiles a list of booleans, where True indicates that the item is a folder
    out = [os.path.isdir(os.path.join(folder, x)) for x in os.listdir(folder)]
    

    # this line can be optimized by using os.path.join instead of string concatenation
    # out2 = list(np.array(os.listdir(folder))[np.logical_not(out)])
    out2 = list(np.array(os.listdir(folder))[np.logical_not(out)]) # is it ok to use numpy here: no, because it is not a core python library
    return(out2)
    
### given folder, return all the files in that folder, as well as in subfolders
def get_all_files(folder : str = None) -> pd.DataFrame:
    """
    # Description
        Given a folder, return all the files in that folder, as well as in subfolders
    # Inputs
        folder: string, the folder to search
                default: None
    # Outputs
        out: pandas DataFrame, the files in the folder, as well as in subfolders
    # Imports
        import pandas as pd
        import numpy as np
    # Example
        >>> # assume there is a folder called "test" in the current directory
        >>> # with files called "test1.txt" and "test2.txt"
        >>> # assume there is a subfolder called "test_sub" in the folder "test"
        >>> # with files called "test_sub1.txt" and "test_sub2.txt"
        >>> get_all_files(folder='test')
        top_level_folder folder file
        0 test test1.txt
        1 test test2.txt
        2 test test_sub test_sub1.txt
        3 test test_sub test_sub2.txt

    """
    # get the subfolders in the top level folder, using the function `get_all_subfolders`
    folder_list = get_all_subfolders(folder)
    
    # initialize the output list
    out_list = []

    # the following line can be optimized by using a list comprehension instead of a for loop:
    # for fold in folder_list:
    #     temp = pd.DataFrame(dict(file=get_files(fold)))
    #     temp['folder'] = fold[len(folder)+1:]
    #     temp['top_level_folder'] = folder
    #     out_list.append(temp['top_level_folder folder file'.split()])

    # this line creates a list of dataframes, where each dataframe contains the files in a subfolder
    out_list = [pd.DataFrame(dict(file=get_files(fold)))['file'] for fold in folder_list]

    # this line adds a column to each dataframe in the list, where the column contains the subfolder name
    out_list = [x.assign(folder=fold[len(folder)+1:]) for x in out_list]

    # this line adds a column to each dataframe in the list, where the column contains the top level folder name
    out_list = [x.assign(top_level_folder=folder) for x in out_list]

    # this line concatenates the dataframes in the list into a single dataframe
    out_df = pd.concat(out_list).reset_index(drop=True)
       
    # filter out non-excel files by looking for the string ".xls" in the file name
    # (will get files with the extensions .xls, .xlsx, .xlsm, etc.)
    is_excel_ind = out_df.file.str.lower().str.contains('.xls')

    # filter out files with some variation of the word "deal"
    deal_filter = out.file.str.lower().str.contains('deal')

    # filter out files with some variation of the word "final"
    final_filter = out.file.str.lower().str.contains('final')
    
    # return the filtered dataframe
    return(out)
    
### test filename to find patterns for clues re: what type of contract
def parse_filename_test(x : str = None, search_list : list = None) -> pd.DataFrame:
    """
    # Description
        Given a filename, return a dataframe with a column for each search term,
        where the value is True if the search term is in the filename, and False
        otherwise
    # Inputs
        x:  string, the filename
            default: None
        search_list: list, the search terms
            default: None
    # Outputs
        out: pandas DataFrame, a dataframe with a column for each search term,
            where the value is True if the search term is in the filename, and False
            otherwise
    # Imports
        import pandas as pd
    # Example
        >>> parse_filename_test(x='test1.txt', search_list=['test', '1'])
        is_test is_1
        0 True True
    """
    # this line can be optimized by using a list comprehension instead of a for loop:
    # qry = pd.DataFrame(dict(x=x))
    # for term in search_list:
    #     qry['is_{}'.format(term)] = x.str.lower().str.contains(term)
    # optimized version:
    qry = pd.DataFrame(dict(x=x))
    qry = qry.assign(**{'is_{}'.format(term): x.str.lower().str.contains(term) for term in search_list})

    # the optimized version works by creating a dictionary, where the keys are the column names
    # and the values are the values for the columns. the dictionary is then passed to the `assign`
    # function, which creates the columns in the dataframe.

    # this line drops the column 'x' and
    # returns True if any of the columns are True
    out = qry.drop(columns='x').any(axis=1)

    # return the output dataframe
    return(out)

def get_page(sht : wb.Sheet = None, max_columns : int = 32) -> list:
    """
    # Description
        Given a sheet, return a list of lists, where each list is a row in the sheet
    # Inputs
        sht:  wb.Sheet, the sheet
            default: None
        max_columns: int, the maximum number of columns to read
            default: 32
    # Outputs
        page: list, a list of lists, where each list is a row in the sheet
    # Imports
        import pandas as pd
        import numpy as np
    """
    # initialize the output list
    page = []

    # loop through the rows in the sheet
    for r in sht.rows():

        # initialize the counter
        counter = 1

        # initialize the row list
        row = []

        # loop through the cells in the row
        for cell in r:

            # increment the counter
            counter = counter + 1

            # if the counter is less than or equal to 32 (the maximum number of columns to read)
            # is given by the input `max_columns`
            if counter <= max_columns:

                # if the value of the cell is not None
                if cell.v is not None:
                    # append the value of the cell to the row list
                    row.append(cell.v)

        # append the row list to the output list
        page.append(row)

    # return the output list
    return(page)
    
def format_ds_data(x : str = None) -> str:
    """
    # Description
        Given a value, return the value in a format suitable for the data source
    # Inputs
        x:  string, the value
            default: None
    # Outputs
        out: string, the value in a format suitable for the data source
    # Imports
        import pandas as pd
    # Example
        >>> format_ds_data(x='test1.txt')
        'test1.txt'
    """
    # first test if the value is a string
    if type(x)==str:

        # if the value is a string, and the string is '0x7', return 0
        if x=='0x7':
            return(0)

        # if the value is a string, and the string is empty, return 'N/A'
        elif x=='':
            return('N/A')

        # if the value is a nonempty string that is not '0x7', return the string
        # but strip any leading or trailing whitespace
        else:
            return(x.strip())

    # if the value is a float
    elif type(x)==float:

        # if the value is less than 1, round to 4 decimal places
        if x<1:
            return(round(x, 4))

        # if the value is greater than or equal to 1, round to 3 decimal places
        else:
            return(round(x, 3))

    # otherwise, return the value
    else:
        return(x)
        
def parse_key_contract_terms(page : list = None, n_layers : int = 8) -> dict:
    """
    # Description
        Given a list of lists, where each list is a row in the sheet, return a dictionary
        with the key contract terms
    # Inputs
        page: list, a list of lists, where each list is a row in the sheet
            default: None
        n_layers: int, the number of layers in the sheet
            default: 8
    # Outputs
        d: dict, a dictionary with the key contract terms
    # Imports
        import pandas as pd
        import numpy as np
    """
    # initialize the output dictionary and the list of other terms
    d = {}
    others = []

    # loop through the rows in the sheet
    # this loop can be optimized by using a list comprehension instead of a for loop:
    # for row in page:
    #     if len(row)==0:
    #         pass
    #     else:
    #         if row[0]=="Summary Economics":
    #             break
    #         elif row[0]=="Key Contract Terms":
    #             pass
    #         elif len(row)==1:
    #             row[0] = row[0].replace("(%)", "%")
    #             d[row[0].replace(' ', '_').lower()] = 'N/A'
    #         elif row[1]=="CRM ID:":
    #             row[0] = row[0].replace("(%)", "%")
    #             d['client_name'] = row[0] if row[0] != '' else 'N/A'
    #             d['crm_id'] = row[2] if row[2] != '' else 'N/A'
    #             d['contract_name'] = row[4] if row[4] != '' else 'N/A'
    #             d['mga'] = row[6] if row[6] != '' else 'N/A'
    #             d['broker']=row[8] if row[8] != '' else 'N/A'
    #         elif len(row)==9:
    #             row[0] = row[0].replace("(%)", "%")
    #             item = row[0].replace(' ', '_').lower()
    #             d[item] = {}
    #             for layer in range(8):
    #                 d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1+layer])
    #         elif len(row)==25:
    #             row[0] = row[0].replace("(%)", "%")
    #             ## these have two values, and an extra cell for a delimiter between the range
    #             item1 = row[0][:row[0].find("/")].lower().replace(" ", "_")
    #             item2 = row[0][1+row[0].find("/"):].lower().replace(" ", "_")
    #             d[item1], d[item2] = {}, {}
    #             for layer in range(8):
    #                 d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][(3*layer)])
    #                 d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][2+(3*layer)])
    #         elif len(row)==17:
    #             row[0] = row[0].replace("Brok on R/I Prem (%)", "Brok on RI Prem (%)")
    #             row[0] = row[0].replace("(%)", "%")
                
    #             ## these have two values, but no delimeter
    #             if row[0].find('/') != -1:
    #                 item1 = row[0][:row[0].find("/")].lower().replace(" ", "_")
    #                 item2 = row[0][1+row[0].find("/"):].lower().replace(" ", "_")
    #                 d[item1], d[item2] = {}, {}
    #                 for layer in range(8):
    #                     d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][(2*layer)])
    #                     d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
    #             else:
    #                 item1 = row[0].lower().replace(" ", "_") + '_basis'
    #                 item2 = row[0].lower().replace(" ", "_") 
    #                 d[item1], d[item2] = {}, {}
    #                 for layer in range(8):
    #                     d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][(2*layer)])
    #                     d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
    #         elif len(row)==10:
    #             row[0] = row[0].replace("(%)", "%")
    #             item = row[0].replace(' ', '_').lower()
    #             d[item] = {}
    #             for layer in range(8):
    #                 d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1+layer])
    #             d[item]['note'] = format_ds_data(row[9])
    #         else:
    #             others.append(row)
    # this is the list comprehension version of the above for loop
    
    # loop over the rows in the sheet, skipping empty rows
    for row in [row for row in page if len(row) != 0]:

        # if the row is the summary economics row, break the loop
        if row[0] == "Summary Economics":
            break

        # if the row is the key contract terms row, skip it
        elif row[0] == "Key Contract Terms":
            pass

        # if the row is a single cell, replace the spaces with underscores and add it to the dictionary
        elif len(row) == 1:

            # if the first cell has a percent sign in parentheses, replace it with a percent sign
            row[0] = row[0].replace("(%)", "%")

            # add the key to the dictionary
            d[row[0].replace(' ', '_').lower()] = 'N/A'

        # if the second cell is CRM ID, then we are in the header row,
        # and we need to add the client name, CRM ID, contract name, MGA,
        # and broker to the dictionary
        elif row[1] == "CRM ID:":

            # if the first cell has a percent sign in parentheses, replace it with a percent sign
            row[0] = row[0].replace("(%)", "%")

            # add the client name, CRM ID, contract name, MGA, and broker to the dictionary
            # if the value is empty, replace it with N/A
            d['client_name'] = row[0] if row[0] != '' else 'N/A'
            d['crm_id'] = row[2] if row[2] != '' else 'N/A'
            d['contract_name'] = row[4] if row[4] != '' else 'N/A'
            d['mga'] = row[6] if row[6] != '' else 'N/A'
            d['broker'] = row[8] if row[8] != '' else 'N/A'
        
        # if the row has 9 cells, then we are in the summary economics row
        elif len(row) == 9:

            # if the first cell has a percent sign in parentheses, replace it with a percent sign
            row[0] = row[0].replace("(%)", "%")

            # replace the spaces with underscores and add the key to the dictionary
            item = row[0].replace(' ', '_').lower()

            # initialize the dictionary for the item
            d[item] = {}

            # loop over the layers and add the values to the dictionary (max 8 layers)
            for layer in range(n_layers):

                # if the value is empty, replace it with N/A
                d[item]['layer_{}'.format(layer + 1)] = format_ds_data(row[1 + layer])

        elif len(row) == 25:
            # if the first cell has a percent sign in parentheses, replace it with a percent sign
            row[0] = row[0].replace("(%)", "%")

            ## these have two values, and an extra cell for a delimiter between the range
            # if the first cell has a slash, then we have two values, so we need to split them

            item1 = row[0][:row[0].find("/")].lower().replace(" ", "_")

            # if the first cell has a slash, then we have two values, so we need to split them
            item2 = row[0][1 + row[0].find("/"):].lower().replace(" ", "_")

            # initialize the dictionaries for the items
            d[item1], d[item2] = {}, {}

            # loop over the layers and add the values to the dictionary (max `n_layers` layers)
            for layer in range(n_layers):

                # if the value is empty, replace it with N/A
                d[item1]['layer_{}'.format(layer + 1)] = format_ds_data(row[1:][(3 * layer)])
                d[item2]['layer_{}'.format(layer + 1)] = format_ds_data(row[1:][2 + (3 * layer)])

        elif len(row) == 17:
            row[0] = row[0].replace("Brok on R/I Prem (%)", "Brok on RI Prem (%)")
            row[0] = row[0].replace("(%)", "%")

            ## these have two values, but no delimeter
            if row[0].find('/') != -1:

                # if the first cell has a slash, then we have two values, so we need to split them
                item1 = row[0][:row[0].find("/")].lower().replace(" ", "_")
                item2 = row[0][1 + row[0].find("/"):].lower().replace(" ", "_")

                # initialize the dictionaries for the items
                d[item1], d[item2] = {}, {}
                
                # loop over the layers and add the values to the dictionary (max `n_layers` layers)
                for layer in range(n_layers):
                    d[item1]['layer_{}'.format(layer + 1)] = format_ds_data(row[1:][(2 * layer)])
                    d[item2]['layer_{}'.format(layer + 1)] = format_ds_data(row[1:][1 + (2 * layer)])
    
    # add the other rows to the list of other rows
    out = dict(dat=d, others=others)

    # return the dictionary
    return(out)
    
def parse_summary_economics(page : list = None, n_layers : int = 8) -> dict:
    """
    # Description
        This function parses the summary economics from the deal sheet.
    # Inputs
        page : list
            The list of rows from the deal sheet.
        n_layers : int
            The number of layers in the deal sheet.
            Default is 8.
    # Outputs
        out : dict
            A dictionary containing the summary economics.
    """
    # initialize the dictionary with the client name, CRM ID, contract name, MGA, and broker
    key_contract_terms = parse_key_contract_terms(page=page, n_layers=n_layers)

    # initialize the dictionary
    d = key_contract_terms['dat']

    # initialize the list of other rows
    others = []

    # initialize the number of layers
    used_cols = list(key_contract_terms['dat'].keys())

    # initialize the flag for the summary economics
    hit_sum_econ = False

    # loop over the rows
    for row in page:

        # if the row has 0 cells, then we are in the summary economics row, so
        if len(row)==0:
            pass
        else:

            # if `hit_sum_econ` is `True`, then we are in the summary economics row
            if hit_sum_econ:

                # if the first cell is a string
                if type(row[0])==str:

                    # if the first cell has a subject business UOBG
                    if row[0]=="Subject Business UOBG":
                        break

                    # if the first cell is not "Subject Business UOBG"
                    else:
                        # replace "Ult." with "Ult"
                        row[0] = row[0].replace('Ult.', 'Ult')
                        
                        ## ROW LENGTH 10
                        # if the row has either 10 or 11 cells
                        if len(row) in [n_layers+2, n_layers+3]:

                            # remove the spaces and parentheses from the first cell
                            item = row[0].lower().replace(" ", "_").replace("_(1:", "_1:")

                            # initialize the dictionary for the item
                            d[item] = {}

                            # loop over the layers and add the values to the dictionary (max 8 layers)
                            for layer in range(n_layers):

                                # add the values to the dictionary
                                d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][layer])

                            # if the row has exactly 10 cells, then the last cell is the combined value
                            if len(row)==n_layers+2:

                                # add the combined value to the dictionary
                                d[item]['combined'] = format_ds_data(row[len(row)-1])

                            # if the row has exactly 11 cells, then the last two cells are the capital and the ROE
                            else:
                                d[item]['capital'] = format_ds_data(row[len(row)-2])
                                d[item]['roe'] = format_ds_data(row[len(row)-1])
                        
                        ## ROW LENGTH 18 & 19
                        # if the row has either 18 or 19 cells
                        elif len(row) in [(2*(n_layers)+2), (2*(n_layers)+3)]:

                            # if the first cell has a slash
                            if row[0].find("/") != -1:

                                # replace the spaces and parentheses in the first cell, to get the first item
                                item1 = row[0][:row[0].find("/")].lower().replace(" ", "_").replace("_(1:", "_1:")

                                # if the first item is either "Risk Limit Share" or "Occurrence Limit Share", then the second cell is
                                # the "ROL" version of the first cell
                                if item1 in ['risk_limit_share', 'occurrence_limit_share']:
                                    item2 = '{}_rol'.format(item1)

                                # otherwise, the second cell is the first cell with the slash removed
                                # and the spaces and parentheses replaced
                                else:
                                    item2 = row[0][1+row[0].find("/"):].lower().replace(" ", "_").replace("_(1:", "_1:")
                                
                                # initialize the dictionaries for the items
                                d[item1], d[item2] = {}, {}

                                # loop over the layers and add the values to the dictionary (max `n_layers` layers)
                                for layer in range(n_layers):

                                    # add the values to the dictionary
                                    d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][2*layer])
                                    d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
                                
                                # if the row has exactly 19 cells, then the last two cells are the combined values
                                # for the first and second items (over all layers)
                                if len(row)==(2*(n_layers)+3):
                                    d[item1]['combined'] = format_ds_data(row[len(row)-2])
                                    d[item2]['combined'] = format_ds_data(row[len(row)-1])

                                # if the row has exactly 18 cells, then the last cell is the combined value
                                # for the first item (over all layers), and there is no combined value for
                                # the second item
                                else:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-1])

                            # if the first cell does not have a slash
                            else:

                                # replace the spaces and parentheses in the first cell, to get the first item
                                item1 = row[0][:row[0].find("/")].lower().replace(" ", "_").replace("_(1:", "_1:")
                                item2 = '{}_pct'.format(item1)
                                d[item1], d[item2] = {}, {}

                                # loop over the layers and add the values to the dictionary (max `n_layers` layers)
                                for layer in range(n_layers):

                                    # add the values to the dictionary
                                    d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][2*layer])
                                    d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
                                
                                # if the row has exactly 19 cells, then the last two cells are the combined values
                                if len(row)==(2*(n_layers)+3):
                                    d[item1]['combined'] = format_ds_data(row[len(row)-2])
                                    d[item2]['combined'] = format_ds_data(row[len(row)-1])
                                
                                # if the row does not have exactly 19 cells, then the last cell is the combined value
                                else:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-1])
                        
                        # if the row has 9 cells, the first is the name of the item, and the rest are the values
                        # for each layer (max 8 layers)
                        elif len(row)==(n_layers + 1):

                            # replace the spaces and parentheses in the first cell, to get the item
                            item = row[0].lower().replace(" ", "_").replace("_(1:", "_1:")
                            
                            # initialize the dictionary for the item
                            d[item] = {}

                            # loop over the layers and add the values to the dictionary (max `n_layers` layers)
                            for layer in range(n_layers):

                                # add the values to the dictionary
                                d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][layer])
                        
                        # if the row length is not yet given, then add it to the list of "others"
                        # which will be returned at the end, to be parsed manually
                        else:
                            others.append(row)

            # if we have hit the "Summary Economics" section, then continue
            else:
                if row[0] == 'Summary Economics':
                    hit_sum_econ = True
                else:
                    pass
    # return the dictionary of data and the list of "others"
    return(dict(dat=d, others=others))
    
def parse_subject_business_uobg(page : list = None) -> dict:
    """
    # Description
    Parses the "Subject Business" and "UOBG" sections of the DS page.

    # Inputs
    page : list
        The list of rows from the DS page.


    """
    key_contract_terms = parse_summary_economics(page)
    d = key_contract_terms['dat']
    others = []
    used_cols = list(key_contract_terms['dat'].keys())
    hit_uobg = False
    for row in page:
        if len(row)==0:
            pass
        else:
            if hit_uobg:
                if type(row[0])==str:
                    if row[0]=="Deposit Prem Schedule":
                        break
                    elif row[0] in ["<Select UOBG>", 'Total']:
                        pass
                    else:
                        row[0] = row[0].replace('Ult.', 'Ult')
                        ## ROW LENGTH 10
                        if len(row) in [10, 11]:
                            item = 'uobg_{}'.format(counter)
                            d[item] = {}
                            for layer in range(8):
                                d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][layer])
                            if len(row)==10:
                                d[item]['combined'] = format_ds_data(row[len(row)-1])
                            else:
                                d[item]['capital'] = format_ds_data(row[len(row)-2])
                                d[item]['roe'] = format_ds_data(row[len(row)-1])
                        ## ROW LENGTH 18 & 19
                        elif len(row) in [18, 19]:
                            if row[0].find("/") != -1:
                                item1 = 'uobg_{}'.format(counter)
                                item2 = 'uobg_{}_pct'.format(counter)
                                d[item1], d[item2] = {}, {}
                                for layer in range(8):
                                    d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][2*layer])
                                    d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
                                if len(row)==19:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-2])
                                    d[item2]['combined'] = format_ds_data(row[len(row)-1])
                                else:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-1])
                            else:
                                item1 = 'uobg_{}'.format(counter)
                                item2 = 'uobg_{}_pct'.format(counter)
                                d[item1], d[item2] = {}, {}
                                for layer in range(8):
                                    d[item1]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][2*layer])
                                    d[item2]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][1+(2*layer)])
                                if len(row)==19:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-2])
                                    d[item2]['combined'] = format_ds_data(row[len(row)-1])
                                else:
                                    d[item1]['combined'] = format_ds_data(row[len(row)-1])
                        elif len(row)==9:
                            item = 'uobg_{}'.format(counter)
                            d[item] = {}
                            for layer in range(8):
                                d[item]['layer_{}'.format(layer+1)] = format_ds_data(row[1:][layer])
                        else:
                            others.append(row)
                    counter = counter + 1
            else:
                if row[0] == 'Subject Business UOBG':
                    hit_uobg = True
                    counter = 1
                else:
                    pass
    return(dict(dat=d, others=others))
    
def find_num_layers(d : dict = None) -> int:
    """
    """
    prem_series = pd.Series(d['ult_cin_re_premiu'])
    idx = prem_series.index.tolist()
    
    for i in range(len(idx)-1):
        if prem_series[idx[:i+1]].sum().round(0)==round(prem_series[len(idx)-1], 0):
            return(i+1)
    return(999)
    
def rename_column(c):
    ## several things always get renamed
    new_col_name = (c
                    .replace('effective', 'effective_date')
                    .replace('expire_date', 'expiration_date')
                    .replace('qs%_', 'qs')
                    .replace('_placement%', 'placement%')
                    .replace('reinsurance_rat', 'reinsurance_rate')
                    .replace('th%', 'th')
                    .replace('ceding_com_', 'ceding_comm_'))
    
    ## remove final character unless specific sequence of characters
    if new_col_name.find("1:")==-1:
        new_col_name = new_col_name.replace(":", "")
    if new_col_name.find("(")==-1:
        new_col_name = new_col_name.replace(")", "")
        
    ## if missing final letter, add it
    if new_col_name.find('bonus')==-1:
        new_col_name = new_col_name.replace("bonu", "bonus")
    if new_col_name.find('capital')==-1:
        new_col_name = new_col_name.replace("capita", "capital")
    if new_col_name.find('premium')==-1:
        new_col_name = new_col_name.replace('premiu', 'premium')
    if new_col_name.find('ratio')==-1:
        new_col_name = new_col_name.replace('rati', 'ratio')
    if new_col_name.find('adjustment')==-1:
        new_col_name = new_col_name.replace('adjustmen', 'adjustment')
    if new_col_name.find('brokerage')==-1:
        new_col_name = new_col_name.replace('brokerag', 'brokerage')
    if new_col_name.find('expense')==-1:
        new_col_name = new_col_name.replace('expens', 'expense')
    if new_col_name.find('profit')==-1:
        new_col_name = new_col_name.replace('profi', 'profit')
    if new_col_name.find('discounted')==-1:
        new_col_name = new_col_name.replace('discounte', 'discounted')
        
    ## add closing parentheses if needed
    if (new_col_name.find("(")!=-1) and (new_col_name.find(")")==-1):
        new_col_name = new_col_name + ")"
        
    ## change something to something new, may or may not be missing final letter
    if new_col_name.find('commission')==-1:
        new_col_name = new_col_name.replace('commissio', 'comm')
    else:
        new_col_name = new_col_name.replace('commission', 'comm')
        
    ## once all this is done, combine a few things:
    new_col_name = (new_col_name.replace('brokerage_%', 'brokerage_pct'))

    return(new_col_name)
    
def parsed_to_df(d):
    cols_0 = list(d.keys())
    cols = ['layer'] + cols_0
    
    try:
        num_layers = find_num_layers(d)
#         print('num_layers: {}'.format(num_layers))
        if num_layers==999:
            print('Unable to find the number of layers for this treaty. (1000)')
            try:
                print('client_name: {}\ncrm_id: {}\ncontract_name: {}'.format(d['client_name'], d['crm_id'], d['contract_name']))
            except:
                print('Not in the correct form: (1001)')
            return(999)
        else:
            try:
                df_list = pd.DataFrame(dict(layer=list(range(1, num_layers+1)))).set_index('layer')
            except:
                print('(1003)')
            for c in cols_0:
                new_col_name = rename_column(c)
                if type(d[c])==dict:
                    layers = list(range(1, num_layers+1))
                    value = [d[c]['layer_{}'.format(l)] for l in layers]
                else:
                    layers = list(range(1, num_layers+1))
                    value= [d[c] for _ in layers]
                try:
                    df_list[new_col_name] = value
                except:
                    print(c)
            return(df_list.reset_index())
    except:
        print('Unable to find the number of layers for this treaty. (9999)')
        print('client_name: {}\ncrm_id: {}\ncontract_name: {}'.format(d['client_name'], d['crm_id'], d['contract_name']))
        return(999)
        
def one_file_type1(file):
    try:
        wb = pyxlsb.open_workbook(file)
    except:
        print('{} is not found'.format(file))
    try:
        sht = wb.get_sheet('Contract Summary')
        page = get_page(sht)
    except:
        print('{} is not found does not have a Contract Summary tab'.format(file))
    try:
        d =  parse_subject_business_uobg(page)
        df = parsed_to_df(d['dat'])
        return(df)
    except:
        print('{} had another error. who knows what???'.format(file))
        
def calc_remaining_time(pct_complete, start_time):
    import datetime
    cur_time = datetime.datetime.now()
    cur_hour, cur_min, cur_sec = cur_time.hour, cur_time.minute, cur_time.second
    cur_s = (3600 * cur_hour) + (60 * cur_min) + (cur_sec)
    
    start_hour, start_min, start_sec = start_time.hour, start_time.minute, start_time.second
    start_s = (3600 * start_hour) + (60 * start_min) + (start_sec)
    
    sec_so_far = cur_s - start_s
    ult_sec = sec_so_far / pct_complete
    sec_resv = ult_sec - sec_so_far
    min_resv = np.floor(sec_resv / 60)
    sec_resv2 = round(sec_resv - (60 * min_resv), 0)
    
    return(min_resv, sec_resv2, sec_so_far)
    
    
def get_uobg_lookup(file=r'O:\PARM\Corporate Actuarial\Reserving\Assumed Reinsurance\data\uobg_mapping\ds_uobg_lookup_20220727.xlsx', 
                    sheet_name='Sheet1'):
    df = pd.read_excel(file, sheet_name)
    
    for c in 'major_lob subline business_segment business_sub_segment business_group class_group pr_non_pr cm_occ uobg_desc uobg_desc2'.split():
        df[c] = df[c].astype('category')
        
    df['uobg'] = df['uobg'].astype(float)
    return(df)

def all_files(files, show_every=5):
    dflist = []
    others = []
    n = len(files)
    counter=1
    
    ## loop through the files, reading one by one
    start_time = datetime.now()
    for f in files:
        if (counter % show_every == 0) or (counter == n):
            m, s, sofar = calc_remaining_time(counter / n, start_time)
            print('{} / {} ({}%) complete -- est. {}m{}s remaining'.format(counter, n, round(100 * (counter / n), 1), int(m), int(s)))
        temp = one_file_type1(f)
        if type(temp)==int:
            ## this only happens when there is an error, so add this to the list of "others"
            others.append(f)
        else:
            dflist.append(temp)
        counter = counter + 1
        
    ## take the list of single-file df's from last step and append to a single table
    df=pd.concat(dflist).reset_index(drop=True)
    
    ## format the columns
    df['one'], df['zero'], df['blank'], df['na'] = 1, 0, '', 'N/A' # series for recoding
    for c in df.columns.tolist():
        if c in ['one', 'zero', 'blank', 'na']:                    # don't recode the recoding cols
            pass
        else:
            df[c] = df['na'].where(df[c].isna(), other=df[c])
    df.drop('one zero blank na'.split(), 1, inplace=True)          # remove the series used for recoding 
    
    ## join the uobg_desc field
    ulk = uobg_lookup['uobg uobg_desc'.split()].set_index('uobg')
    for i in range(1, 9):
        df = df.set_index('uobg_{}'.format(i))
        df = df.join(ulk, how='left')
        df = df.rename(columns={'uobg_desc':'uobg_{}_desc'.format(i)})
        df = df.reset_index().rename(columns={'index':'uobg_{}'.format(i)})
        print(df.head())
    
    ## return a dictionary with both the data and the "others" list of files that didn't work correctly
    out = dict(df=df, others=others)
    return(out)
    
def main():

    ### df with all the files
    df = get_all_files(folder)


    ### is it an excel filename? 
    df['is_excel'] = df['file'].str.contains('.xls')

    ### run many different queries
    qry = (df
           .assign(has_deal=df.file.str.lower().str.contains('deal'))
           .assign(has_summary=df.file.str.lower().str.contains('summary'))
           .assign(not_db=np.logical_not(df.file.str.lower().str.contains('database')))
           .assign(not_db2=np.logical_not(df.file.str.lower().str.contains('db')))
           .assign(not_template=np.logical_not(df.file.str.lower().str.contains('template')))
    #        .assign(not_ds_folder=df.folder.ne('Deal Sheets'))
           .assign(not_templates_folder=np.logical_not(df.folder.str.lower().str.contains('template')))
           
           .drop('top_level_folder folder'.split(), 1)
           .all(axis=1, bool_only=True)
          )
    df1 = (df
           .assign(is_final=df.file.str.lower().str.contains('final'))
           .assign(is_cas=df.file.str.lower().str.contains('cas'))
           .loc[qry, :]
           .reset_index(drop=True)
           .drop('is_excel', 1)
          )

    ### xlsb file
    xlsb_list=['.xlsb']
    df1['is_xlsb'] = parse_filename_test(df1.file, xlsb_list)

    ### does the filename mention quota share?
    qs_list = 'quota qs'.split()        ## list of keywords
    df1['is_qs'] = parse_filename_test(df1.file, qs_list)

    ### retro?
    retro_list = ['retro']
    df1['is_retro'] = parse_filename_test(df1.file, retro_list)

    ### surplus share
    ss_list = [' ss']
    df1['is_surplus_share'] = parse_filename_test(df1.file, ss_list)

    ### does the filename mention catastrophes?
    cat_list = 'cat catastrophe'.split()
    df1['is_cat'] = parse_filename_test(df1.file, cat_list)

    ### does the filename mention property?
    prop_list = 'prop property'.split()
    df1['is_property'] = parse_filename_test(df1.file, prop_list)

    ### does the filename mention WC?
    wc_list = ['wc', 'work comp', 'workers comp', 'workers compensation']
    df1['is_wc'] = parse_filename_test(df1.file, wc_list)

    ### does the filename mention xol?
    xol_list = ['xol']
    df1['is_xol'] = parse_filename_test(df1.file, xol_list)

    ### per policy
    per_policy_list=['per policy']
    df1['is_per_policy'] = parse_filename_test(df1.file, per_policy_list)

    ### per risk
    per_risk_list=['per risk', 'ppr']
    df1['is_per_risk'] = parse_filename_test(df1.file, per_risk_list)

    ### aggregate
    agg_list=['agg']
    df1['is_agg'] = parse_filename_test(df1.file, agg_list)

    ### fannie/freddie
    fannie_freddie_list=['fannie', 'freddie']
    df1['is_fannie_freddie'] = parse_filename_test(df1.file, fannie_freddie_list)

    ### cirt
    cirt_list=['cirt']
    df1['is_cirt'] = parse_filename_test(df1.file, cirt_list)

    ### create files df that holds filenames
    files = df1.loc[df1.is_xlsb, :]['top_level_folder folder file'.split()]
    files['filepath'] = files.apply(lambda x: '{}\\{}'.format(x[0], x[1]), axis=1)
    files['filename'] = files.apply(lambda x: '{}\\{}\\{}'.format(x[0], x[1], x[2]), axis=1)

    ### read in uobg lookup df
    uobg_lookup = get_uobg_lookup()

    ### run process 
    d = all_files(files.filename.tolist())

    ### output table
    n = datetime.now()
    yr, mth, d, h, m, s = n.year, n.month, n.day, n.hour, n.minute, n.second

    ts = '{}_{}_{}_{}_{}_{}'.format(yr,
                                    ('0' if mth < 10 else '') + str(mth),
                                    ('0' if d < 10 else '') + str(d),
                                    ('0' if h < 10 else '') + str(h),
                                    ('0' if m < 10 else '') + str(m),
                                    ('0' if s < 10 else '') + str(s))
    d['df'].to_excel('./ds_data_{}.xlsx'.format(ts))
    
main()