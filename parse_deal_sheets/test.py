#!/usr/bin/env python
# coding: utf-8

# In[474]:


# All links to importing/exporting data subject to change;


# In[475]:


import pandas as pd
import os
import numpy as np
from datetime import date
pd.options.mode.chained_assignment = None # deletes the warning message for duplicated dataframes; not necessary for this code
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# In[476]:


## function that is the main workflow
## each line should be a single function that has a very descriptive name

#def main():
    
#    read_in_user_inputs_file()
    

#ask_for_month_year()
    
#    read_in_prior_month_alloc_file()
    
    
    
    
    #output ibnr alloc table


# In[477]:


month_file = int(float(input("Month: ")))
year_file =int(float(input("Year: ")))


# In[478]:


# time variable assigning section
if (month_file-1)//3 == 0:
    quarter = 4
else:
    quarter = (month_file-1)//3
if month_file%12>=9:
    quarter_previous = 2
elif month_file%12>=6:
    quarter_previous = 1
elif month_file%12>=3:
    quarter_previous = 4
else: 
    quarter_previous = 3

if quarter ==4:
    year = year_file-1
else:
    year = year_file
if month_file<=3:
    Cm = 0
elif month_file<=6:
    Cm = 3
elif month_file<=9:
    Cm = 6
else: 
    Cm = 9
if month_file<=5 :
    year_previous = year_file-1
else: 
    year_previous = year_file
if quarter_previous == 4:
    quarter_next = 1
    year_next = year_previous+1
else:
    quarter_next = quarter_previous+1
    year_next = year_previous

dig2yr = year_previous-2000 # last 2 digits of year; update in 78 years


# In[479]:


quarter


# In[480]:


# Data Import Section
importdata = r'C:\Users\KAN\Downloads\user inputs template1.xlsx' #loc subject to change
schp_data = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'schp_data_loss')
schp_adj =pd.read_excel('{z}'.format(z = importdata), sheet_name = 'schp_data_adj')
#dcce_picks = pd.read_excel('{z}'.format(z = importdata), sheet_name ='Selected_DCC_ratio' )
schp_cy_ep = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'CY_EP')
#schp_MRL = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'MRL_cube_premium')
loss_corridor = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'ult_adj')
#loss_picks = pd.read_excel('{z}'.format(z = importdata), sheet_name ='Selected_loss_ratio' )
if month_file <=3 :################ MAKES SLIGHT DIFFERENCE; 4,5, ALLOCATION FILE STILL USES MRL NET DIRECT
    schp_MRLnet = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\3Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation 1-{yrf}.xlsb'.format(py = year_file-1, yrf = year_file), sheet_name = 'MRL Cube Net-Direct (Values)', engine='pyxlsb')
link_ratio = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'link_ratio_data_for_python')
ratio_selection = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'stub_loss_ratio')
ep_adj = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'CY_EP_adj')
linename = pd.read_excel('{z}'.format(z = importdata), sheet_name = 'Lines')


# In[ ]:





# In[481]:


#lists -> imported from the user input data file
lines = []
for i in np.arange(len(linename['line of business'])):
    lines.append(linename['line of business'][i])
justline_short = []
for i in np.arange(len(linename['short'])):    
    justline_short.append(linename['short'][i])
noIMline = justline_short.copy()
if 'IM' in noIMline:
     noIMline.remove('IM')
clm = ['type']
for i in np.arange(len(linename['short'])):    
    clm.append(linename['short'][i])
clm.append('All lines')
lineshort = ['AY','type']
for i in np.arange(len(linename['short'])):    
    lineshort.append(linename['short'][i])
lineshort.append('All lines')
d = {}
for i in np.arange(0,len(linename['mrl_asl'])):
    a = linename.loc[i]['short']
    b = linename.loc[i]['mrl_asl']
    d.update({a:b})
drev = {}
for i in np.arange(0,len(linename['mrl_asl'])):
    a = linename.loc[i]['short']
    b = linename.loc[i]['mrl_asl']
    drev.update({b:a})
d1 = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
d2 = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}


# In[483]:


#extract this quarter's link ratio data and last quarter's link ratio data
alldata = link_ratio[(link_ratio['analysis_year'] == year) &(link_ratio['analysis_quarter'] == quarter )]
alldata_previous = link_ratio[(link_ratio['analysis_year'] == year_previous) &(link_ratio['analysis_quarter'] == quarter_previous )]


# In[484]:


#Build loss corridor table
Loss_corridor_adj = pd.DataFrame(columns = lineshort) # set the dataframe to put in the loss corridor adj
Loss_corridor_adj['AY'] = (np.arange(year_file-20,year_file+1))# set AY column as 20-year range from current file year
Loss_corridor_adj.set_index('AY', inplace = True)# set AY as index
for yrr in np.arange(year_file-20, year_file+1):
    for a in justline_short:# create double for loops for all AY's and lob's
            Loss_corridor_adj[a][yrr] = (loss_corridor[(loss_corridor['mrl_asl'] == d[a]) & (loss_corridor['ay'] == yrr)]['amount'].values)
            #plug in the values into the dataframe
Loss_corridor_adj = Loss_corridor_adj[Loss_corridor_adj!=0].astype('float64').fillna(0)
# put the values in integer so that it can be added later


# In[485]:


# extract the selected loss ratio & dcce ratio picks; only used for month1-5
loss_picks = ratio_selection[ratio_selection['type_of_loss'] == 'loss']
dcce_picks = ratio_selection[ratio_selection['type_of_loss'] == 'dcce']


# In[486]:


loss_picks = loss_picks.transpose()# transpose the tables
dcce_picks = dcce_picks.transpose()
loss_picks.columns = loss_picks.loc['mrl_asl']# set the column to mrl_asl codes
dcce_picks.columns = dcce_picks.loc['mrl_asl']


# In[487]:


if month_file <= 3:
    schp_MRLnet = schp_MRLnet.fillna(0) # fill NaN value to 0
    schp_MRLnet.columns = schp_MRLnet.loc[18]# set the columns to mrl_asl code
    schp_MRLnet = schp_MRLnet.iloc[19:57,:19]# set the location; includes current and previous 2 year data for safety
    schp_MRLnet.columns.values[0] = "cy" # set column names
    schp_MRLnet.columns.values[1] = "mytd"
    schp_MRLnet.set_index(schp_MRLnet.iloc[:,0], inplace = True)# set the index to first column


# In[488]:


schp_cy_ep.columns.values[0] = "cy-cm" # set the column name to 'cy-cm'
schp_cy_ep.set_index(schp_cy_ep.iloc[:,0], inplace = True)# set the index to first column


# In[489]:


dflist = [] # blank list
df = pd.DataFrame()# blank df
finalDf = df
for ab in justline_short:
    df1 = alldata[((alldata['item_type'] == 'reported_loss') & (alldata['item_sub_type'] == 'cumulative')& (alldata['analysis_line'] == ab))].reset_index(drop=True)
    df2 = alldata[((alldata['item_type'] == 'paid_loss') & (alldata['item_sub_type'] == 'cumulative')& (alldata['analysis_line'] == ab))].reset_index(drop=True)
    df3 = df1['Value']-df2['Value'] # case reserve amount
    df4 = df[0:21].copy() # create a blank dataframe for template
    df4['Value'] = df3.values
    df4['item_sub_type'] = df3.replace(df3, 'cumulative').values # set 'item_sub_type' to 'cumulative'
    df4['item_type']=df3.replace(df3, 'case reserve') # set 'item_type' to 'case reserve'
    df4['item_row_lookup'] = np.arange(year_file-20,year_file+1) # plug in year(20 year range from current year-input above)
    df4['method_type'] = df3.replace(df3, 'data')# set 'method_type' to 'data'
    df4['analysis_line'] = ab # analysis line name = lob
    dflist.append(df4)
casersv = pd.concat(dflist)


# In[491]:


# Direct Paid DCCE table code

Dcce_table = pd.DataFrame(columns = lineshort) ## assign column names to lob's
def paid_dcce(all):
    for item in lineshort:
        Dcce_table[item] = (alldata[((alldata['item_type'] == 'paid_dcce') & (alldata['item_sub_type'] == 'cumulative')& (alldata['analysis_line'] == item))]['Value'].reset_index(drop=True))
        # assign to import from link ratio data
    Dcce_table['AY'] = (np.arange(year_file-20,year_file+1)) # assign a year column, 20 year range from current year
    Dcce_table['type'] = 0 # add a type column
    Dcce_table['All lines'] =Dcce_table.sum(axis = 1) -Dcce_table['AY'] # assign 'All lines' value
    return Dcce_table
Direct_paid_dcce = paid_dcce(all).set_index('AY')# name change possible here
if quarter ==4: # quarter == 4; alldata is from 4Q of previous year, shift 1 up for current year row; month1-3
    Direct_paid_dcce = Direct_paid_dcce.shift(-1).fillna(0) 
else:
    Direct_paid_dcce = Direct_paid_dcce # else: same
Direct_paid_dcce = Direct_paid_dcce.fillna(0)


# In[492]:


#Qtd paid DCCE table code
# set the code and lines into a dictionary so the corresponding code comes up for each line
# fileloc subject to change
Qtd_paid_dcce_development = pd.DataFrame(columns = lineshort) # assign column names in the DataFrame
Qtd_paid_dcce_development['AY'] = (np.arange(year_file-20,year_file+1)) # assign Year Column
Qtd_paid_dcce_development.set_index('AY', inplace = True) # AY as index
for j in justline_short: # for loop for assigning each line's data
         Qtd_paid_dcce_development[j] = schp_data[(schp_data['Loss Type'] == 'DCC') & (schp_data['MRL_ASL'] == d[j]) & (schp_data['CM'] > Cm)].groupby('AY').sum()['Direct']#.reset_index(drop=True)  
        # assign to import from schp data
Qtd_paid_dcce_development['All lines'] =Qtd_paid_dcce_development.sum(axis = 1) # assign 'All lines' column
Qtd_paid_dcce_development['type'] = 0 # assign 'type' column
Qtd_paid_dcce_development =Qtd_paid_dcce_development.fillna(0)# fill NaN with 0


# In[493]:


# build EP YTD table
EP_YTD  = pd.DataFrame(columns = clm) # set dataframe with column names assigned
cy_ep_ytd = schp_cy_ep[schp_cy_ep['cy-cm'] == '{mm}YTD'.format(mm = d1[month_file])]# indicate the row with EP YTD
for a in noIMline: # IM excluded since not included in CSU Alloc files; can be added by using justline_short
    EP_YTD['{aa}'.format(aa = a)] = cy_ep_ytd[d[a]]# put the data in the dataframe, all the dict, list.. are assigned above
EP_YTD = EP_YTD.fillna(0)
EP_YTD = EP_YTD.reset_index(drop = True)# reset index


# In[494]:


ep_adj_ytd = ep_adj[['mrl_asl','amount', 'type']]
ep_adj_ytd = ep_adj_ytd[ep_adj_ytd['type'] == 'YTD']
ep_adj_ytd = ep_adj_ytd.transpose() # transpose the EP-adjustment table, to set columns as lob's
ep_adj_ytd.columns = ep_adj_ytd.loc['mrl_asl']# set columns as lob's
EP_adj_ytd = pd.DataFrame(columns = clm, index = [0])# set dataframe, same structure as EP_YTD
EP_adj_ytd = EP_adj_ytd.fillna(0)# fill NaN with 0
for a in justline_short:
    EP_adj_ytd[a] = (ep_adj_ytd[d[a]]['amount'] if d[a] in ep_adj_ytd.columns else 0) # plug in the values into the df
EP_YTD = EP_YTD+EP_adj_ytd # add adj to the ep


# In[500]:


# build prior year EP extracted from MRL cube net-direct
if month_file <=3:
    ddf =  pd.DataFrame(columns = clm)# previous year's ep table
    cmytd = 'DecYTD'# uses last year's december data; typically up until March of each year
    prev_mrl = (schp_MRLnet[(schp_MRLnet['cy'] == year_file-1) & (schp_MRLnet['mytd'] == 'DecYTD')]).reset_index(drop=True)
    # last yr's December data from MRL cube net direct [Values]
    prev_mrl.iloc[:,0] = 0 # put 0 in the cy column;
    for a in justline_short:
        if (d[a]/10 - int(d[a]/10)) == 0: # if d[a]/10 is integer, return whole number. else;decimal 
            c = int(d[a]/10)
        else: # d[a]/10 is with decimal, return same
            c = d[a]/10
        ddf[a] = (prev_mrl[('ASL_{aa}'.format(aa = c))] if ('ASL_{aa}'.format(aa = c)) in prev_mrl.columns else 0) # put MRL data in the dataframe
    prev_YTD = ddf.fillna(0)# fill NaN with 0


# In[501]:


prev_YTD


# In[502]:


# Earned premium table from last quarter
ep = pd.DataFrame(columns = lineshort) # set df
def earned_premium(all): # define function
    for item in lineshort:
        # select earned premium data from previous quarter's data
        ep[item] = (alldata_previous[((alldata_previous['item_type'] == 'premium') & (alldata_previous['item_sub_type'] == 'earned')& (alldata_previous['analysis_line'] == item))]['Value'].reset_index(drop=True))
        ep['AY'] = (np.arange(year_file-20,year_file+1))# set Year Column
    return ep
# for 2022 row -> YTD 2022 Earned Premium * if month<=5, ratio =  CSU Ultimate Loss pick - DCCE Ratio Selection tab
                                         # * else: , ratio =  Sel_ult_dcce ratio 

earned_prem = earned_premium(all).set_index('AY').fillna(0).astype('int64') # get rid of NaN and exponents, set index
if month_file<= 5: 
    earned_prem =  earned_prem.shift(-1).fillna(0) # shifts the data up 1 year, if using last year's link ratio file; month1-5
else: 
    earned_prem =  earned_prem
Earned_premium = earned_prem.copy()
if month_file <=3:
    Earned_premium.loc[year_file-1] = prev_YTD.loc[0] 
# assigning previous year value to value calculated from MRL cube net direct for now, based on the formulas in the allocation files
else:
    Earned_premium = Earned_premium
Earned_premium = Earned_premium.fillna(0)
Earned_premium = Earned_premium.astype('int64')


# In[503]:


# selected ultimate dcce ration table from previous quarter
ult_dcce_ratio = pd.DataFrame(columns = lineshort) # set df
def dcce_ratio(all):
    for item in lineshort:
        # select ultimate dcce ratio data from previous quarter's data
        ult_dcce_ratio[item] = (alldata_previous[((alldata_previous['item_type'] == 'paid_dcce') & (alldata_previous['item_sub_type'] == 'selected_ult_loss_ratio')& (alldata_previous['analysis_line'] == item))]['Value'].reset_index(drop=True))
        ult_dcce_ratio['AY'] = (np.arange(year_file-20,year_file+1)) # set Year Column
    return ult_dcce_ratio
sel_dcce_ratio =dcce_ratio(all).fillna(0)#
sel_dcce_ratio =sel_dcce_ratio.set_index('AY')
if year_file != year_previous:# if statement for when previous quarter is last year (for 1Q reports)
    sel_dcce_ratio = sel_dcce_ratio.shift(-1).fillna(0)# shifts the data 1 year, if current quarter is 1; else: doesn't
else: 
    sel_dcce_ratio = sel_dcce_ratio
Selected_DCCE_ratio = sel_dcce_ratio.copy()


# In[504]:


#Selected Direct DCCE Reserve Table
sub = Direct_paid_dcce+Qtd_paid_dcce_development # total paid dcce
sub['type'] = 0 # set the type column value to 0 so that it doesn't shoot error when subtracted
Selected_DCCE_Reserve = (sel_dcce_ratio*Earned_premium - sub).fillna(0).astype('int64').round(-3) # 
# sum of the values from lines; have to be a better way; for loop returns 0 for some reason
for a in justline_short:
    Selected_DCCE_Reserve['All lines'] += Selected_DCCE_Reserve[a]


# In[505]:


# code to extract selected dcce ratio of current year
current_ratio1 = pd.DataFrame(columns = clm, index = {'dcce_ratio'} )
current_ratio = pd.DataFrame(columns = clm)
def current_dcce_ratio():
    for a in noIMline:
        if month_file <= 5: # for quarter 1,2; use ratio selected from previous quarter 
            selection = dcce_picks
            current_ratio1[a].loc['dcce_ratio'] = dcce_picks[d[a]].loc['ratio']#.reset_index(drop=True)
            current_ratio[a] = current_ratio1[a]
            #current_ratio = current_ratio.loc['ratio'].reset_index(drop=True)
        else: # for quarter 3,4; use selected_ultimate_dcce_ratio 
            current_ratio[a] = (alldata_previous[((alldata_previous['item_type'] == 'paid_dcce') & (alldata_previous['item_sub_type'] == 'selected_ult_loss_ratio')& (alldata_previous['analysis_line'] == a)& (alldata_previous['item_row_lookup'] ==year_previous))]['Value'].reset_index(drop=True))

    return current_ratio.fillna(0).reset_index(drop = True)
Selected_DCCE_ratio.loc[year_file] = current_dcce_ratio().loc[0]


# In[506]:


#direct paid dcce of current year
current_paid = pd.DataFrame(columns = clm)
for j in justline_short: # for loop for assigning each line's data
         current_paid[j] = schp_data[(schp_data['Loss Type'] == 'DCC') & (schp_data['MRL_ASL'] == d[j]) & (schp_data['CM'] <= quarter * 3) & (schp_data['AY'] == year)].groupby('AY').sum()['Direct']#.reset_index(drop=True)      
current_paid = current_paid.fillna(0).reset_index(drop = True)
if quarter == 4:
    current_paid.loc[0] = 0
else:
    current_paid = current_paid
# qtd paid dcce of current year
current_qtd = Qtd_paid_dcce_development.loc[year_file].copy()
current_qtd = pd.DataFrame(current_qtd).transpose().reset_index (drop = True)
current_qtd['type'] = 0

# put 2022 data in the paid dcce table
if quarter ==4:
    Direct_paid_dcce = Direct_paid_dcce
else:
    Direct_paid_dcce.loc[year_file] = current_paid.loc[0]

# dcce reserve of current year
curdcc = current_dcce_ratio().reset_index(drop = True)

current_reserve = (EP_YTD*curdcc - current_qtd - current_paid).round(-3)
current_reserve['All lines'] = current_reserve.sum(axis = 1)

# put it into dcce reserve table
Selected_DCCE_Reserve.loc[year_file] =  current_reserve.loc[0]
Selected_DCCE_Reserve = Selected_DCCE_Reserve.round(-3)
# put 2022 selected dcce ratio to ratio table
Selected_DCCE_ratio.loc[year_file] = current_dcce_ratio().loc[0]
# put EP YTD 2022 to earned premium table
Earned_premium.loc[year_file] = EP_YTD.loc[0]
Earned_premium = Earned_premium.round(0)


# In[507]:


# Build Direct Reported Loss table
reported_loss_table = pd.DataFrame() # create a blank DataFrame
def reported_loss(all):
    for item in lineshort:
        reported_loss_table[item] = (alldata[((alldata['item_type'] == 'reported_loss') & (alldata['item_sub_type'] == 'cumulative')& (alldata['analysis_line'] == item))]['Value'].reset_index(drop=True))
        # assign which data to import
    reported_loss_table.columns = lineshort # assign column names to lob's
    reported_loss_table['AY'] = (np.arange(year_file-20,year_file+1)) # assign a year column, 20 year range from current year
    reported_loss_table['All lines'] =reported_loss_table.sum(axis = 1) -reported_loss_table['AY'] # assign 'All lines' value
    return reported_loss_table
Direct_reported_loss = reported_loss(all).round(0).set_index('AY')# name change possible here
if quarter ==4:
    Direct_reported_loss = Direct_reported_loss.shift(-1).fillna(0)
else:
    Direct_reported_loss = Direct_reported_loss.fillna(0)
Direct_reported_loss = Direct_reported_loss.round(0)


# In[508]:


#Build Carried Direct Case Reserve table
carried_case_reserve_table = pd.DataFrame() # create a blank DataFrame
def carried_case_reserve(all):
    for item in lineshort:
        carried_case_reserve_table[item] = (casersv[((casersv['item_type'] == 'case reserve') & (casersv['item_sub_type'] == 'cumulative')& (casersv['analysis_line'] == item))]['Value'].reset_index(drop=True))
        # assign which data to import
    carried_case_reserve_table.columns = lineshort # assign column names to lob's
    carried_case_reserve_table['AY'] = (np.arange(year_file-20,year_file+1)) # assign a year column, 20 year range from current year
    carried_case_reserve_table['All lines'] =carried_case_reserve_table.sum(axis = 1) -carried_case_reserve_table['AY'] # assign 'All lines' value
    return carried_case_reserve_table
Carried_case_reserve = carried_case_reserve(all).round(0).set_index('AY')# name change possible here
Carried_case_reserve = Carried_case_reserve.round(0)
if quarter ==4:
    Carried_case_reserve = Carried_case_reserve.shift(-1).fillna(0)
else:
    Carried_case_reserve = Carried_case_reserve.fillna(0)# 


# In[509]:


# Build Direct Case Reserve schp data table
case_reserve1 = pd.DataFrame(columns = lineshort) # assign column names in the DataFrame
case_reserve1['AY'] = (np.arange(year_file-20,year_file+1)) # assign Year Column
case_reserve1.set_index('AY', inplace = True) 
for j in justline_short: # for loop for assigning each line's data
         case_reserve1[j] = schp_data[(schp_data['Loss Type'] == 'Loss Resv') & (schp_data['MRL_ASL'] == d[j]) & (schp_data['CM'] == month_file)&(schp_data['CY'] == year_file)].groupby('AY').sum()['Direct']  
case_reserve1 =case_reserve1.fillna(0)
# adjustment data
case_reserve_adj = pd.DataFrame(columns = lineshort) # assign column names in the DataFrame
case_reserve_adj['AY'] = (np.arange(year_file-20,year_file+1)) # assign Year Column
case_reserve_adj.set_index('AY', inplace = True) 
for j in justline_short: # for loop for assigning each line's data
         case_reserve_adj[j] = schp_adj[(schp_adj['Loss Type'] == 'Loss Resv') & (schp_adj['ASL'] == d[j]) & (schp_adj['CM'] == month_file)&(schp_adj['CY'] == year_file)].groupby('AY').sum()['Direct']       
case_reserve_adj =case_reserve_adj.fillna(0)
# ultimate case reserve table
Direct_case_reserve =(case_reserve1+case_reserve_adj).fillna(0)
for a in justline_short:
    Direct_case_reserve['All lines'] += Direct_case_reserve[a]
Direct_case_reserve =Direct_case_reserve.round(0)


# In[510]:


# Qtd Direct Paid Loss Development schp data table
Qtd_paid_loss_development1 = pd.DataFrame(columns = lineshort) # assign column names in the DataFrame
Qtd_paid_loss_development1['AY'] = (np.arange(year_file-20,year_file+1)) # assign Year Column
Qtd_paid_loss_development1.set_index('AY', inplace = True) 
for j in justline_short: # for loop for assigning each line's data
         Qtd_paid_loss_development1[j] = schp_data[(schp_data['Loss Type'] == 'Paid Loss') & (schp_data['MRL_ASL'] == d[j]) & (schp_data['CM'] > Cm)&(schp_data['CY'] == year_file)].groupby('AY').sum()['Direct']  
Qtd_paid_loss_development1 =Qtd_paid_loss_development1.fillna(0)
# Qtd Direct Paid Loss Development Adjustment table
Qtd_paid_loss_development_adj = pd.DataFrame(columns = lineshort) # assign column names in the DataFrame
Qtd_paid_loss_development_adj['AY'] = (np.arange(year_file-20,year_file+1)) # assign Year Column
Qtd_paid_loss_development_adj.set_index('AY', inplace = True) 
for j in justline_short: # for loop for assigning each line's data
         Qtd_paid_loss_development_adj[j] = schp_adj[(schp_adj['Loss Type'] == 'Paid Loss') & (schp_adj['ASL'] == d[j]) & (schp_adj['CM'] > Cm)&(schp_adj['CY'] == year_file)].groupby('AY').sum()['Direct']  
Qtd_paid_loss_development_adj =Qtd_paid_loss_development_adj.fillna(0)
Qtd_paid_loss_development = Qtd_paid_loss_development1 + Qtd_paid_loss_development_adj
for a in justline_short:
    Qtd_paid_loss_development['All lines'] += Qtd_paid_loss_development[a]
Qtd_paid_loss_development = Qtd_paid_loss_development.round(0)


# In[512]:


# Qtd Direct Reported Loss Development
def qtd_rep_loss(all):
    Qtd_paid_loss_development['type'] = 0
    Direct_case_reserve['type'] = 0
    Carried_case_reserve['type'] = 0
    qtd_rep_loss = Qtd_paid_loss_development+Direct_case_reserve-Carried_case_reserve
    return qtd_rep_loss
Qtd_reported_loss_development = qtd_rep_loss(all)


# In[513]:


# selected ultimate loss ratio table from previous quarter
ult_loss_ratio = pd.DataFrame(columns = lineshort) # set df
def loss_ratio(all):
    for item in lineshort:
        # select ultimate dcce ratio data from previous quarter's data
        ult_loss_ratio[item] = (alldata_previous[((alldata_previous['item_type'] == 'reported_loss') & (alldata_previous['item_sub_type'] == 'selected_ult_loss_ratio')& (alldata_previous['analysis_line'] == item))]['Value'].reset_index(drop=True))
        ult_loss_ratio['AY'] = (np.arange(year_file-20,year_file+1)) # set Year Column
    return ult_loss_ratio
sel_loss_ratio =loss_ratio(all).fillna(0)#
sel_loss_ratio =sel_loss_ratio.set_index('AY')
if year_file != year_previous:# if statement for when previous quarter is last year (for 1Q reports)
    sel_loss_ratio = sel_loss_ratio.shift(-1).fillna(0)# shifts the data 1 year, if current quarter is 1; else: doesn't
else: 
    sel_loss_ratio = sel_loss_ratio
Selected_loss_ratio = sel_loss_ratio.copy()


# In[515]:


# build current year's selected loss ratio
loss_ratio_current = pd.DataFrame(columns = clm )
loss_selection = pd.DataFrame(columns = clm, index = {'loss_ratio'})
def current_loss_ratio():
    for a in noIMline:
        if month_file<=5: # month1-5, use stub loss ratio
            loss_selection.loc['loss_ratio'][a] = loss_picks.loc['ratio'][d[a]]
            loss_ratio_current[a] = loss_selection[a].reset_index(drop=True).fillna(0)
        else: # else: selected_ultimate_dcce_ratio 
            loss_ratio_current[a] = (alldata_previous[((alldata_previous['item_type'] == 'reported_loss') & (alldata_previous['item_sub_type'] == 'selected_ult_loss_ratio')& (alldata_previous['analysis_line'] == a)& (alldata_previous['item_row_lookup'] == year_file))]['Value'].reset_index(drop=True))

    return loss_ratio_current.fillna(0)
Selected_loss_ratio.loc[year_file] = current_loss_ratio().loc[0]


# In[516]:


dcce_adj = Loss_corridor_adj.copy()
dcce_adj = dcce_adj*0


# In[517]:


def pull_reserve(premium, selected_ratio, qtd_paid,  Direct_paid, data_adj):
    premium['type'] = 0
    qtd_paid['type'] = 0 
    selected_ratio['type'] = 0
    Direct_paid['type'] = 0
    data_adj['type'] = 0
    Reserve = (premium.round(0)*selected_ratio - qtd_paid.round(0) - Direct_paid.round(0) + data_adj.round(0)).round(-3).fillna(0)
    for a in justline_short:
        Reserve['All lines'] += Reserve[a]
    return Reserve
Selected_Direct_IBNR =  pull_reserve(Earned_premium, Selected_loss_ratio, Qtd_reported_loss_development, Direct_reported_loss, Loss_corridor_adj )
# make a function for dcce/IBNR to come out in type automatically


# In[519]:


#for i in np.arange(year_file-20,year_file+1):
#    if i<2022:
#         Selected_Direct_IBNR['Cyber'][i] = 0
############# NOT GENERAL###########ADD LATER


# In[520]:


print("Ignore dtype, displaying below negative values in DCCE Reserve") 
print("Name = lines of businesses") 
print("Returning Series[] means there is no negative values in that line of business")
for ln in justline_short: 
    no = Selected_DCCE_Reserve[Selected_DCCE_Reserve[ln]<0][ln].count() 
    yrloc = Selected_DCCE_Reserve.index[Selected_DCCE_Reserve[ln]<0] 
    print(Selected_DCCE_Reserve[ln],', type = DCCE Reserve')
    print('\n ')
    print(Selected_DCCE_Reserve[Selected_DCCE_Reserve[ln]<0][ln],', type = DCCE Reserve',',mrl_asl =' ,d[ln])
    print("Press Enter for no change")
    for a in yrloc: 
        Selected_DCCE_Reserve[ln].loc[a] = (input("Change year {k} value to: ".format(k = a)) or Selected_DCCE_Reserve[ln].loc[a]) 
    print(' \n')

print(' \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n ') 
print("Ignore dtype, displaying below negative values in IBNR Reserve") 
print("Name = lines of businesses") 
print("Returning Series[] means there is no negative values in that line of business")
for ln in justline_short: 
    no = Selected_Direct_IBNR[Selected_Direct_IBNR[ln]<0][ln].count()
    yrloc = Selected_Direct_IBNR.index[Selected_Direct_IBNR[ln]<0]
    print(Selected_Direct_IBNR[ln],', type = IBNR Reserve')
    print('\n')
    print(Selected_Direct_IBNR[Selected_Direct_IBNR[ln]<0][ln],', type = IBNR Reserve',',mrl_asl =' ,d[ln])
    print("Press Enter for no change")
    for a in yrloc: 
        Selected_Direct_IBNR[ln].loc[a] = (input("Change year {k} value to: ".format(k = a)) or Selected_Direct_IBNR[ln].loc[a]) 
    print('\n')


# In[521]:


#Set variables to find the required allocation files
if month_file>1: # for previous cm allocation file
    prevcm = month_file -1
    prevcmyr = year_file
else:
    prevcm = 12
    prevcmyr = year_file -1
if prevcm%12>=9:
    cmloc = 2
elif prevcm%12>=6:
    cmloc = 1
elif prevcm%12>=3:
    cmloc = 4
else: 
    cmloc = 3
if prevcm%12<=5:
    cmlocyr = year_file -1
else: 
    cmlocyr = year_file

if month_file<=3:# for previous cq allocation file
    prevcq = 12
    prevcqyr = year_file -1
    cqlocyr = year_file -1
elif month_file<=6:
    prevcq = 3
    prevcqyr = year_file
    cqlocyr = year_file -1
elif month_file<=9:
    prevcq = 6
    prevcqyr = year_file
    cqlocyr = year_file
else:
    prevcq = 9
    prevcqyr = year_file
    cqlocyr = year_file
if prevcq/3-1 != 0:
    cqloc = int(prevcq/3 - 1)
else: 
    cqloc = 4

prevcy = 12# for previous cy allocation file
prevcyyr = year_file -1


# In[522]:


#Import Data; previous cm, cq, cy
prevcmdata = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\{pq}Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(pq = cmloc, py = cmlocyr, mf = prevcm,yrf = prevcmyr),engine='pyxlsb', sheet_name = 'IBNR Analysis')
prevcqdata = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\{pq}Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(pq = cqloc, py = cqlocyr, mf = prevcq,yrf = prevcqyr),engine='pyxlsb', sheet_name = 'IBNR Analysis')
prevcydata = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\3Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(py = prevcyyr, mf = prevcy,yrf = prevcyyr),engine='pyxlsb', sheet_name = 'IBNR Analysis')
prevcmdcce = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\{pq}Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(pq = cmloc, py = cmlocyr, mf = prevcm,yrf = prevcmyr),engine='pyxlsb', sheet_name = 'DCCE Reserve Analysis')
prevcqdcce = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\{pq}Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(pq = cqloc, py = cqlocyr, mf = prevcq,yrf = prevcqyr),engine='pyxlsb', sheet_name = 'DCCE Reserve Analysis')
prevcydcce = pd.read_excel(r'O:\STAFFHQ\SYMDATA\Actuarial\Reserving Applications\IBNR Allocation\3Q{py} Analysis\CSU\Reserve Allocation\CSU Allocation {mf}-{yrf}.xlsb'.format(py = prevcyyr, mf = prevcy,yrf = prevcyyr),engine='pyxlsb', sheet_name = 'DCCE Reserve Analysis')


# In[523]:


# set columns to lobs and AY
prevcmdata.columns = prevcmdata.loc[2]
prevcqdata.columns = prevcqdata.loc[2]
prevcydata.columns = prevcydata.loc[2]
# locate selected ibnr table from each allocation files
cmibnr1 = prevcmdata.iloc[3:23,1:16].reset_index(drop = True)
cqibnr1 = prevcqdata.iloc[3:23,1:16].reset_index(drop = True)
cyibnr1 = prevcydata.iloc[3:23,1:16].reset_index(drop = True)
prevcmdcce.columns = prevcmdcce.loc[2]
prevcqdcce.columns = prevcqdcce.loc[2]
prevcydcce.columns = prevcydcce.loc[2]
# locate selected dcce table from each allocation files
cmdcce1 = prevcmdcce.iloc[3:23,1:16].reset_index(drop = True)
cqdcce1 = prevcqdcce.iloc[3:23,1:16].reset_index(drop = True)
cydcce1 = prevcydcce.iloc[3:23,1:16].reset_index(drop = True)
# allocate QTD Direct Reported Loss Table
cmrep_loss_development1  = prevcmdata.iloc[28:48,1:16].reset_index(drop = True)
cyrep_loss_development1 = prevcydata.iloc[28:48,1:16].reset_index(drop = True)
# allocate direct reported loss of previous cy
cy_rep_loss1 = prevcydata.iloc[132:152,1:16].reset_index(drop = True)
# allocate QTD Direct paid dcce Table
cmrep_dcce_development1  =prevcmdcce.iloc[28:48,1:16].reset_index(drop = True)
cyrep_dcce_development1 = prevcydcce.iloc[28:48,1:16].reset_index(drop = True)
# allocate direct paid dcce of previous cy
cy_rep_dcce1 = prevcydcce.iloc[54:74,1:16].reset_index(drop = True)


# In[524]:


cmrep_loss_development1


# In[525]:


# lists of lines that are both in this year & last time period's file; used to construct last time period's data;
cylist = [] # empty list
for a in (cydcce1.columns & linename['mrl_asl']): # for lob's that are both in this&last year's file:
    cylist.append(drev[a]) # cylist contains lob's
cmlist = []
for a in (cmdcce1.columns & linename['mrl_asl']):
    cmlist.append(drev[a])
cqlist = []
for a in (cqdcce1.columns & linename['mrl_asl']):
    cqlist.append(drev[a])


# In[526]:


# set empty template structure
cmibnr = pd.DataFrame(columns = lineshort)
cqibnr = pd.DataFrame(columns = lineshort)
cyibnr = pd.DataFrame(columns = lineshort)
cmdcce = pd.DataFrame(columns = lineshort)
cqdcce = pd.DataFrame(columns = lineshort)
cydcce = pd.DataFrame(columns = lineshort)
loss_develop_m= pd.DataFrame(columns = lineshort)
loss_develop_y= pd.DataFrame(columns = lineshort)
paid_dcce_cm = pd.DataFrame(columns = lineshort)
paid_dcce_cy = pd.DataFrame(columns = lineshort)


# In[527]:


#Direct paid dcce from prev cy
cyrepdcc1 = pd.DataFrame(columns= lineshort)
for a in cylist:
        cyrepdcc1[a]  = (cy_rep_dcce1[d[a]])

cyrepdcc1['AY'] = cy_rep_dcce1['AY']
cyrepdcc1 = cyrepdcc1.fillna(0)
for a in justline_short:
    cyrepdcc1['All lines'] += (cyrepdcc1[a])
cyrepdcc1 = cyrepdcc1.set_index('AY')


# In[528]:


## MTD Direct Paid DCCE
for a in cmlist:
    paid_dcce_cm[a] = cmrep_dcce_development1[d[a]]
paid_dcce_cm['AY'] = cmrep_dcce_development1['AY']
paid_dcce_cm = paid_dcce_cm.fillna(0)
for a in justline_short:
    paid_dcce_cm['All lines'] += paid_dcce_cm[a]
paid_dcce_cm = paid_dcce_cm.set_index('AY')
def cmresultdevcc():
    Qtd_paid_dcce_development['type'] = 0
    if month_file in {1,4,7,10}:
        aaz = Qtd_paid_dcce_development.copy()
    else:    
        aaz = Qtd_paid_dcce_development - paid_dcce_cm 
        aaz = aaz.fillna(0)
    if year_file not in paid_dcce_cm.index:
        aaz.loc[year_file] = Qtd_paid_dcce_development.loc[year_file]
    aaz['type'] = 0
    return aaz
cmrdcce_development = cmresultdevcc()


# In[529]:


# QTD Direct Paid DCCE
cqrdcce_development = Qtd_paid_dcce_development.copy()# already calculated


# In[530]:


# YTD Direct Paid DCCE
for a in cylist:
    paid_dcce_cy[a] = cyrep_dcce_development1[d[a]]
paid_dcce_cy['AY'] = cyrep_dcce_development1['AY']
paid_dcce_cy = paid_dcce_cy.fillna(0)
for a in justline_short:
    paid_dcce_cy['All lines'] += paid_dcce_cy[a]
paid_dcce_cy = paid_dcce_cy.set_index('AY')
def cyresultdevcc():
    Qtd_paid_dcce_development['type'] = 0
    Direct_paid_dcce['type'] = 0
    if month_file == 1:
        aaz = Qtd_paid_dcce_development.copy()
    else:
        aaz = Qtd_paid_dcce_development +Direct_paid_dcce - paid_dcce_cy - cyrepdcc1
        aaz = aaz.fillna(0)
    if year_file not in paid_dcce_cy.index:
        aaz.loc[year_file] = Qtd_paid_dcce_development.loc[year_file]+Direct_paid_dcce.loc[year_file]
    aaz['type'] = 0
    return aaz
cyrdcce_development = cyresultdevcc()


# In[531]:


#Direct rep loss from prev cy
cyrep1 = pd.DataFrame(columns= lineshort)
for a in cylist:
    cyrep1[a] = cy_rep_loss1[d[a]]
cyrep1['AY'] = cy_rep_loss1['AY']
cyrep1 = cyrep1.fillna(0)
for a in justline_short:
    cyrep1['All lines'] += cyrep1[a]
cyrep1 = cyrep1.set_index('AY')


# In[532]:


month_file in {1,4,7,10}


# In[533]:


#MTD Incremental Direct Case Incurred Losses
for a in cmlist:
    loss_develop_m[a] = cmrep_loss_development1[d[a]]
loss_develop_m['AY'] = cmrep_loss_development1['AY']
loss_develop_m = loss_develop_m.fillna(0)
for a in justline_short:
    loss_develop_m['All lines'] += loss_develop_m[a]
loss_develop_m = loss_develop_m.set_index('AY')
def cmresultdev():
    Qtd_reported_loss_development['type'] = 0
    Direct_reported_loss['type'] = 0
    if month_file in {1,4,7,10}:
        aaz = Qtd_reported_loss_development.copy()
    else:
        aaz = Qtd_reported_loss_development - loss_develop_m 
        aaz = aaz.fillna(0)
    if year_file not in loss_develop_m.index:
        aaz.loc[year_file] = Qtd_reported_loss_development.loc[year_file]
    aaz['type'] = 0
    return aaz
cmrloss_development = cmresultdev()


# In[534]:


cmrloss_development


# In[535]:


#QTD Incremental Direct Case Incurred Losses
cqrloss_development = Qtd_reported_loss_development.copy() # already calculated


# In[536]:


#YTD Incremental Direct Case Incurred Losses
for a in cylist:
    loss_develop_y[a] = cyrep_loss_development1[d[a]]
loss_develop_y['AY'] = cyrep_loss_development1['AY']
loss_develop_y = loss_develop_y.fillna(0)
for a in justline_short:
    loss_develop_y['All lines'] += loss_develop_y[a]
loss_develop_y = loss_develop_y.set_index('AY')
def cyresultdev():
    Selected_DCCE_Reserve['type'] = 0
    if month_file ==1:
        aaz = Qtd_reported_loss_development.copy()
    else:
        aaz = Qtd_reported_loss_development+Direct_reported_loss - loss_develop_y- cyrep1
        aaz = aaz.fillna(0)
    if year_file not in loss_develop_y.index:
        aaz.loc[year_file] = Qtd_reported_loss_development.loc[year_file]+Direct_reported_loss.loc[year_file]
    aaz['type'] = 0
    return aaz
cyrloss_development = cyresultdev()


# In[537]:


Selected_Direct_IBNR['type'] = 0


# In[538]:


# MTD Direct IBNR change
Selected_Direct_IBNR = Selected_Direct_IBNR.astype('float64')
for a in cmlist:
    cmibnr[a] = cmibnr1[d[a]]
cmibnr['AY'] = cmibnr1['AY']
cmibnr = cmibnr.fillna(0)
for a in justline_short:
    cmibnr['All lines'] += cmibnr[a]
cmibnr = cmibnr.set_index('AY')
def cmresultibnr():
    Selected_Direct_IBNR['type'] = 0
    aaz = Selected_Direct_IBNR - cmibnr
    aaz = aaz.fillna(0)
    if year_file not in cmibnr.index:
        aaz.loc[year_file] = Selected_Direct_IBNR.loc[year_file]
    aaz['type'] = 0
    return aaz
cmribnr = cmresultibnr()


# In[539]:


Loss_corridor_adj


# In[540]:


# QTD Direct IBNR change
for a in cqlist:
    cqibnr[a] = cqibnr1[d[a]]
cqibnr['AY'] = cqibnr1['AY']
cqibnr = cqibnr.fillna(0)
for a in justline_short:
    cqibnr['All lines'] += cqibnr[a]
cqibnr = cqibnr.set_index('AY')
def cqresultibnr():
    Selected_Direct_IBNR['type'] = 0
    aaz = Selected_Direct_IBNR - cqibnr
    aaz = aaz.fillna(0)
    if year_file not in cqibnr.index:
        aaz.loc[year_file] = Selected_Direct_IBNR.loc[year_file]
    aaz['type'] = 0
    return aaz
cqribnr = cqresultibnr()


# In[541]:


# YTD Direct IBNR change
for a in cylist:
    cyibnr[a] = cyibnr1[d[a]]
cyibnr['AY'] = cyibnr1['AY']
cyibnr = cyibnr.fillna(0)
for a in justline_short:
    cyibnr['All lines'] += cyibnr[a]
cyibnr = cyibnr.set_index('AY')
def cyresultibnr():
    Selected_Direct_IBNR['type'] = 0
    aaz = Selected_Direct_IBNR - cyibnr
    aaz = aaz.fillna(0)
    if year_file not in cyibnr.index:
        aaz.loc[year_file] = Selected_Direct_IBNR.loc[year_file]
    aaz['type'] = 0
    return aaz
cyribnr = cyresultibnr()


# In[542]:


# MTD Direct DCCE change
Selected_DCCE_Reserve = Selected_DCCE_Reserve.astype('float64')
for a in cmlist:
    cmdcce[a] = cmdcce1[d[a]]
cmdcce['AY'] = cmdcce1['AY']
cmdcce = cmdcce.fillna(0)
for a in justline_short:
    cmdcce['All lines'] += cmdcce[a]
cmdcce = cmdcce.set_index('AY')
def cmresultdcc():
    Selected_DCCE_Reserve['type'] = 0
    aaz = Selected_DCCE_Reserve - cmdcce
    aaz = aaz.fillna(0)
    if year_file not in cmdcce.index:
        aaz.loc[year_file] = Selected_DCCE_Reserve.loc[year_file]
    aaz['type'] = 0
    return aaz
cmrdcce = cmresultdcc()


# In[543]:


# QTD Direct DCCE change

for a in cqlist:
    cqdcce[a] = cqdcce1[d[a]]
cqdcce['AY'] = cqdcce1['AY']
cqdcce = cqdcce.fillna(0)
for a in justline_short:
    cqdcce['All lines'] += cqdcce[a]
cqdcce = cqdcce.set_index('AY')
def cqresultdcc():
    Selected_DCCE_Reserve['type'] = 0
    aaz = Selected_DCCE_Reserve - cqdcce
    aaz = aaz.fillna(0)
    if year_file not in cqdcce.index:
        aaz.loc[year_file] = Selected_DCCE_Reserve.loc[year_file]
    aaz['type'] = 0
    return aaz
cqrdcce = cqresultdcc()


# In[544]:


# YTD Direct DCCE change
for a in cylist:
    cydcce[a] = cydcce1[d[a]]
cydcce['AY'] = cydcce1['AY']
cydcce = cydcce.fillna(0)
for a in justline_short:
    cydcce['All lines'] += cydcce[a]
cydcce = cydcce.set_index('AY')
def cyresultdcc():
    Selected_DCCE_Reserve['type'] = 0
    aaz = Selected_DCCE_Reserve - cydcce
    aaz = aaz.fillna(0)
    if year_file not in cydcce.index:
        aaz.loc[year_file] = Selected_DCCE_Reserve.loc[year_file]
    aaz['type'] = 0
    return aaz
cyrdcce = cyresultdcc()


# In[545]:


# Build Loss&DCCE Development table
MTD_development = cmribnr+cmrdcce+cmrloss_development+cmrdcce_development
QTD_development = cqribnr+cqrdcce+cqrloss_development+cqrdcce_development
YTD_development = cyribnr+cyrdcce+cyrloss_development+cyrdcce_development


# In[546]:


ep_adj_mtd = ep_adj[['mrl_asl','amount', 'type']]
ep_adj_mtd = ep_adj_mtd[ep_adj_mtd['type'] == 'MTD']
ep_adj_mtd = ep_adj_mtd.transpose() # transpose the EP-adjustment table, to set columns as lob's
ep_adj_mtd.columns = ep_adj_mtd.loc['mrl_asl']# set columns as lob's
EP_adj_mtd = pd.DataFrame(columns = clm, index = [0])# set dataframe, same structure as EP_YTD
EP_adj_mtd = EP_adj_mtd.fillna(0)# fill NaN with 0
for a in justline_short:
    EP_adj_mtd[a] = (ep_adj_mtd[d[a]]['amount'] if d[a] in ep_adj_mtd.columns else 0) # plug in the values into the df


# In[547]:


# MTD Direct Earned Premium
mtd_ep  = pd.DataFrame(columns = clm)
cy_ep_mtd = schp_cy_ep[schp_cy_ep['cy-cm'] == '{mm}'.format(mm = d2[month_file])]
for a in cmlist:
    mtd_ep['{aa}'.format(aa = a)] = cy_ep_mtd[d[a]]
mtd_ep = mtd_ep.fillna(0)
mtd_ep = mtd_ep.reset_index(drop = True)
mtd_ep = mtd_ep+EP_adj_mtd


# In[548]:


ep_adj_qtd = ep_adj[['mrl_asl','amount', 'type']]
ep_adj_qtd = ep_adj_qtd[ep_adj_qtd['type'] == 'QTD']
ep_adj_qtd = ep_adj_qtd.transpose() # transpose the EP-adjustment table, to set columns as lob's
ep_adj_qtd.columns = ep_adj_qtd.loc['mrl_asl']# set columns as lob's
EP_adj_qtd = pd.DataFrame(columns = clm, index = [0])# set dataframe, same structure as EP_YTD
EP_adj_qtd = EP_adj_qtd.fillna(0)# fill NaN with 0
for a in justline_short:
    EP_adj_qtd[a] = (ep_adj_qtd[d[a]]['amount'] if d[a] in ep_adj_qtd.columns else 0) # plug in the values into the df


# In[549]:


# QTD Direct Earned Premium
qtd_ep  = pd.DataFrame(columns = clm)
cy_ep_qtd = schp_cy_ep[schp_cy_ep['cy-cm'] == '{mm}QTD'.format(mm = d1[month_file])]
for a in cqlist:
    qtd_ep['{aa}'.format(aa = a)] = cy_ep_qtd[d[a]]
qtd_ep = qtd_ep.fillna(0)
qtd_ep = qtd_ep.reset_index(drop = True)
qtd_ep = qtd_ep+EP_adj_qtd


# In[550]:


qtd_ep


# In[551]:


# YTD Direct Earned Premium
#ytd_ep  = pd.DataFrame(columns = clm)
#cy_ep_ytd = schp_cy_ep[schp_cy_ep['cy-cm'] == '{mm}YTD'.format(mm = d1[month_file])]
#for a in cylist:
#    ytd_ep['{aa}'.format(aa = a)] = cy_ep_ytd[d[a]]
#ytd_ep = ytd_ep.fillna(0)
#ytd_ep = ytd_ep.reset_index(drop = True)


# In[552]:


ytd_ep = EP_YTD.copy()


# In[553]:


# MTD Direct incurred loss ratio
mtd_incurred_loss_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     mtd_incurred_loss_ratio[a] = (cmribnr+cmrloss_development)[a]/int(mtd_ep[a])
mtd_incurred_loss_ratio = mtd_incurred_loss_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0))


# In[554]:


# QTD Direct incurred loss ratio
qtd_incurred_loss_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     qtd_incurred_loss_ratio[a] = (cqribnr+cqrloss_development)[a]/int(qtd_ep[a])
qtd_incurred_loss_ratio = qtd_incurred_loss_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0))


# In[555]:


ytd_ep


# In[556]:


# YTD Direct incurred loss ratio
ytd_incurred_loss_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     ytd_incurred_loss_ratio[a] = (cyribnr+cyrloss_development)[a]/int(ytd_ep[a])
ytd_incurred_loss_ratio = ytd_incurred_loss_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(7)


# In[557]:


# MTD Direct incurred dcce ratio
mtd_incurred_dcce_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     mtd_incurred_dcce_ratio[a] = (cmrdcce+cmrdcce_development)[a]/int(mtd_ep[a])
mtd_incurred_dcce_ratio = mtd_incurred_dcce_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[558]:


# QTD Direct incurred dcce ratio
qtd_incurred_dcce_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     qtd_incurred_dcce_ratio[a] = (cqrdcce+cqrdcce_development)[a]/int(qtd_ep[a])
qtd_incurred_dcce_ratio = qtd_incurred_dcce_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[559]:


# YTD Direct incurred dcce ratio
ytd_incurred_dcce_ratio = pd.DataFrame(columns=clm)
for a in justline_short:
     ytd_incurred_dcce_ratio[a] = (cyrdcce+cyrdcce_development)[a]/int(ytd_ep[a])
ytd_incurred_dcce_ratio = ytd_incurred_dcce_ratio.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[560]:


# MTD Direct incurred dcce ratio
mtd_incurred_ratio_both = pd.DataFrame(columns=clm)
for a in justline_short:
     mtd_incurred_ratio_both[a] = (MTD_development)[a]/int(mtd_ep[a])
mtd_incurred_ratio_both = mtd_incurred_ratio_both.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[561]:


# QTD Direct incurred dcce ratio
qtd_incurred_ratio_both = pd.DataFrame(columns=clm)
for a in justline_short:
     qtd_incurred_ratio_both[a] = (QTD_development)[a]/int(qtd_ep[a])
qtd_incurred_ratio_both = qtd_incurred_ratio_both.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[562]:


# YTD Direct incurred dcce ratio
ytd_incurred_ratio_both = pd.DataFrame(columns=clm)
for a in justline_short:
     ytd_incurred_ratio_both[a] = (YTD_development)[a]/int(ytd_ep[a])
ytd_incurred_ratio_both = ytd_incurred_ratio_both.fillna(0).replace((np.inf, -np.inf), (0, 0)).round(6)


# In[563]:


#rounding section
Direct_paid_dcce = Direct_paid_dcce.round(0)
Qtd_paid_dcce_development = Qtd_paid_dcce_development.round(0)
Selected_DCCE_Reserve = Selected_DCCE_Reserve.round(-3)


# In[564]:


# Name assigining section
# just assigning type column for all tables
Selected_loss_ratio['type'] = 'Selected_loss_ratio'
Direct_reported_loss['type'] = 'Direct_reported_loss'
Carried_case_reserve['type'] = 'Carried_case_reserve'
Direct_case_reserve['type'] = 'Direct_case_reserve'
Qtd_reported_loss_development['type'] = 'Qtd_reported_loss_development'
Loss_corridor_adj['type'] = 'Loss_corridor_adj'
Selected_Direct_IBNR['type'] = 'Selected_Direct_IBNR'
Earned_premium['type'] = 'Earned_premium'
Qtd_paid_dcce_development['type'] = 'Qtd_paid_dcce_development'
Qtd_paid_loss_development['type'] = 'Qtd_paid_loss_development'
Selected_loss_ratio['type'] = 'Selected_loss_ratio'
Qtd_reported_loss_development['type'] = 'Qtd_reported_loss_development'
Direct_case_reserve['type'] = 'Direct_case_reserve'
Direct_paid_dcce['type'] = 'Direct_paid_dcce'
Selected_DCCE_Reserve['type'] = 'Selected_DCCE_Reserve'
Selected_DCCE_ratio['type'] = 'Selected_DCCE_ratio'
Earned_premium['type'] = 'Earned_premium'

cmribnr['type'] = 'MTD Direct IBNR change'
cqribnr['type'] = 'QTD Direct IBNR change'
cyribnr['type'] = 'YTD Direct IBNR change'
cmrdcce['type'] = 'MTD Direct DCCE Reserve change'
cqrdcce['type'] = 'QTD Direct DCCE Reserve change'
cyrdcce['type'] = 'YTD Direct DCCE Reserve change'
cmrloss_development['type'] = 'MTD Incremental Direct Case Incurred Losses'
cqrloss_development['type'] = 'QTD Incremental Direct Case Incurred Losses'
cyrloss_development['type'] = 'YTD Incremental Direct Case Incurred Losses'
cmrdcce_development['type'] = 'MTD Direct Paid DCCE'
cqrdcce_development['type'] = 'QTD Direct Paid DCCE'
cyrdcce_development['type'] = 'YTD Direct Paid DCCE'
MTD_development['type'] = 'MTD Loss&DCCE Development'
QTD_development['type'] = 'QTD Loss&DCCE Development'
YTD_development['type'] = 'YTD Loss&DCCE Development'
mtd_ep['type'] = 'MTD Direct Earned Premium'
qtd_ep['type'] = 'QTD Direct Earned Premium'
ytd_ep['type'] = 'YTD Direct Earned Premium'
mtd_incurred_loss_ratio['type'] = 'MTD Direct Incurred Loss Ratio'
qtd_incurred_loss_ratio['type'] = 'QTD Direct Incurred Loss Ratio'
ytd_incurred_loss_ratio['type'] = 'YTD Direct Incurred Loss Ratio'
mtd_incurred_dcce_ratio['type'] = 'MTD Direct Incurred DCCE Ratio'
qtd_incurred_dcce_ratio['type'] = 'QTD Direct Incurred DCCE Ratio'
ytd_incurred_dcce_ratio['type'] = 'YTD Direct Incurred DCCE Ratio'
mtd_incurred_ratio_both['type'] = 'MTD Direct Incurred Loss&DCCE Ratio'
qtd_incurred_ratio_both['type'] = 'QTD Direct Incurred Loss&DCCE Ratio'
ytd_incurred_ratio_both['type'] = 'YTD Direct Incurred Loss&DCCE Ratio'


# In[565]:


# list all the functions 
types = [Direct_paid_dcce, Qtd_paid_loss_development , Qtd_paid_dcce_development, Selected_DCCE_ratio, Earned_premium, Selected_DCCE_Reserve, Direct_reported_loss, Carried_case_reserve, Direct_case_reserve, Qtd_reported_loss_development, Selected_loss_ratio, Loss_corridor_adj, Selected_Direct_IBNR, cmribnr,cqribnr, cyribnr, cmrdcce, cqrdcce, cyrdcce, cmrloss_development, cqrloss_development, cyrloss_development, cmrdcce_development, cqrdcce_development, cyrdcce_development, MTD_development, QTD_development, YTD_development, mtd_ep, qtd_ep, ytd_ep, mtd_incurred_loss_ratio, qtd_incurred_loss_ratio, ytd_incurred_loss_ratio, mtd_incurred_dcce_ratio, qtd_incurred_dcce_ratio, ytd_incurred_dcce_ratio, mtd_incurred_ratio_both, qtd_incurred_ratio_both, ytd_incurred_ratio_both]
types1 = types.copy() # make a copy of all the tables


# In[566]:


def colist(line):
    for i in np.arange(0,len(types)):
        types1[i] = pd.DataFrame(columns = ['type','lob','mrl_asl','Value'])
        types1[i]['type'] = types[i]['type']
        types1[i]['lob'] = line
        types1[i]['Value'] = types[i][line]
        types1[i]['mrl_asl'] = d[line]
        colist1 = types1.copy()
        colist1 = pd.concat(colist1)
    return colist1


# In[567]:


dddf = []
for l in justline_short:
    dddf.append(colist(l))
colist = pd.concat(dddf)


# In[568]:


colist.index.name = 'AY'


# In[569]:


colist.to_excel(r'C:\Users\KAN\Downloads\movers\Data\IBNR_allocation_analysis_{mmm}_{yyy}.xlsx'.format(mmm = month_file, yyy = year_file), sheet_name = 'data')
# export to excel,fileloc subject to change


# In[570]:


Qtd_reported_loss_development


# In[571]:


Selected_DCCE_Reserve


# In[572]:


#Formulas
#.to_excel('Output_Check_9.xlsx',sheet_name='Table')
#Dcce_table1 = pd.concat([Dcce_table], axis = 1,ignore_index=True) # put together paid dcce of all lob's
#Dcce_table.reset_index(drop=True)
#(earned_prem*sel_dcce_ratio - Direct_paid_dcce-Qtd_paid_dcce_development).fillna(0).astype('int64',-3) 
 


# In[573]:


# Code lists
# alldata   >>>> extracts cum_rep_loss, cum_paid_loss, cum_paid_dcce, ep, sel_ult_ratio, case reserves of all lines
# alldata_previous  >>>> extracts previous quarter's  cum_rep_loss, cum_paid_loss, cum_paid_dcce, ep, sel_ult_ratio, case reserves of all lines
########## DCCE Reserve Analysis tab
# Direct_paid_dcce  >>>>> extracts direct paid dcce of all lines
# Qtd_paid_dcce_development   >>> extracts Qtd Direct Paid DCCE Development
# Selected_DCCE_ratio >>> extracts previous quarter's selected DCCE ratios
# Earned_premium >>> extracts previous quarter's cumulative earned premium
# Selected_DCCE_Reserve >>>> extracts Selected DCCE Reserve Table
# pull_reserve(premium, qtd_paid, selected_ratio, paid_dcce)  >>> estracts the reserve table; each criteria should be the name of each table ex) 

#########IBNR Analysis tab
# Direct_reported_loss  >>>>>>>>> extracts Direct reported loss table
# Direct_reported_loss >>>> extracts Carried Direct Case Reserve table
# Carried_case_reserve >>> extracts Carried Direct Case Reserve from previous quarter end 
# Direct_case_reserve >>> extracts Direct Case Reserves from current month
# Qtd_reported_loss_development >>> extracts Qtd reported loss development table for current month end
# Selected_loss_ratio >>> extracts previous quarter's selected loss ratio
# Loss_corridor_adj >>> pulls Loss corridor adjustment table
#Selected_Direct_IBNR >>> IBNR table


# pull_reserve(Earned_premium, Selected_DCCE_ratio, Qtd_paid_dcce_development, Direct_paid_dcce, dcce_adj) >>> DCCE Reserve table
# pull_reserve(Earned_premium, Selected_loss_ratio, Qtd_reported_loss_development, Direct_reported_loss, Loss_corridor_adj ) >> IBNR table


# In[ ]:




