library(tidyverse)
library(dtplyr)
library(readxl)
library(rstan)
library(stringr)
rstan_options(auto_write=TRUE)
options(mc.cores = parallel::detectCores())

getwd()

source("./src/main/parse_data_functions.R")

# conctenation ftn for headers
cct <- function(t){ifelse(is.na(t), '', ifelse(is.character(t), t, as.character(t)))}

# read in data, produce column names
headers <- read_excel("./2022Q4/data for Andy 4q22.xlsx", sheet='data', col_names = F, n_max = 3) %>%
  t() %>%
  replace_na() 

col_names <- apply(headers, 1, function(x){paste(c(cct(x[1]), cct(x[2]), cct(x[3])), sep=' ')}) %>%
  apply(2, function(x){paste0(c(x[1], x[2], x[3]))})
col_names <-  col_names[1, ] %>% 
  str_c(" ") %>% 
  str_c(col_names[2, ]) %>% 
  str_c(".") %>% 
  str_c(ifelse(
    col_names[3,]=="9.3000000000000007", 
    "9.30", 
    ifelse(
      col_names[3,]=="6.3",
      "6.30",
      col_names[3,]
      )
  ))

# read prior parameter estimates
prior_df <- read_excel("./2022Q4/2021q4_estimates.xlsx", sheet='estimates')


# read in data, give it those names
df <- read_excel("./2022Q4/data for Andy 4q22.xlsx", sheet='data', col_names = col_names, skip=4) %>%
  
  # rename non-loss columns
  rename(lob=" .LOB", group=" Grouping.For modeling", cre_id=" .CinFin #", sap_id=" .SAP #", deal_name=" .Deal Name") %>%
  rename(eff_date=" .Eff. Date", treaty_year=" .Treaty Year", premium=" .Premium") %>%
  
  # drop empty columns
  select(-c(" ....39"," ....9")) %>% 
  
  # pivot
  pivot_longer(names(select(., -c(lob, group, cre_id, sap_id, deal_name, eff_date, treaty_year, premium)))) %>%
  
  # parse `name` column
  separate(name, c("type", NA, "calendar_date"), sep=" ") %>%
  
  # parse `calendar_date` column
  separate(calendar_date, c("cy", "cm", NA))

df %>% head

# build treaty_id lookup
treaty_id_lookup <- df %>%
  select(cre_id, sap_id, deal_name, eff_date, treaty_year, lob, group, premium) %>%
  unique() %>%
  arrange(eff_date, deal_name) %>%
  mutate(treaty_month=eff_date %>% month()) %>%
  mutate(treaty_quarter=case_when(
    month(eff_date)== 1 ~ 1
    , month(eff_date)== 2 ~ 1
    , month(eff_date)== 3 ~ 1
    , month(eff_date)== 4 ~ 2
    , month(eff_date)== 5 ~ 2
    , month(eff_date)== 6 ~ 2
    , month(eff_date)== 7 ~ 3
    , month(eff_date)== 8 ~ 3
    , month(eff_date)== 9 ~ 3
    , month(eff_date)== 10 ~ 4
    , month(eff_date)== 11 ~ 4
    , month(eff_date)== 12 ~ 4
    )) %>%
  
  # join in prior parameter estimates
  left_join(filter(prior_df, param=="warp") %>% select(-param) %>% rename(warp_mean='mean', warp_var='var'), by='group') %>%
  left_join(filter(prior_df, param=="theta") %>% select(-param) %>% rename(theta_mean='mean', theta_var='var'), by='group') %>%
  left_join(filter(prior_df, param=="elr") %>% select(-param) %>% rename(elr_mean='mean', elr_var='var'), by='group')

treaty_id_lookup %>% head

df %>% head()

# add id column
treaty_id_lookup$treaty_id <- treaty_id_lookup %>% row.names()

# join to df, drop all except treaty_id
model_data <- df %>% 
  left_join(treaty_id_lookup, by=c('cre_id', 'sap_id', 'deal_name', 'eff_date', 'treaty_year', 'lob', 'group', 'premium')) %>%
  
  # recode 1 for reported, 2 for paid, 0 for other
  mutate(type_of_loss = type) %>%
  
  # recode cy, cm to be numeric
  mutate(cy=as.numeric(cy), cm=as.numeric(cm), treaty_id=as.numeric(treaty_id)) %>%
  
  # only need a few columns
  select(treaty_id, type_of_loss, premium, treaty_year, treaty_quarter, cy, cm, value) %>%
  
  # resort
  arrange(type_of_loss, treaty_id, premium, treaty_year, treaty_quarter, cy, cm) %>%
  
  # add development period
  mutate(dev_month_qtr=12*(cy-treaty_year) + (cm - (3*treaty_quarter))) %>%
  mutate(dev_month_yr=12*(cy-treaty_year) + cm) %>%
  
  # re-pivot to have separate reported loss/paid loss columns
  pivot_wider(id_cols=c(treaty_id, treaty_year, treaty_quarter, premium, cy, cm, dev_month_yr, dev_month_qtr), names_from=type_of_loss) %>%
  
  # rename paid/rpt loss columns
  rename(paid_loss="Paid", reported_loss="Rtd") %>%
  
  # make 0's into 0.1's, so nothing involving logs will error out
  mutate(paid_loss=ifelse(paid_loss==0, 0.1, paid_loss), reported_loss=ifelse(reported_loss==0, 0.1, reported_loss)) %>%
  
  # add prior_dev_month columns
  # group treaties together
  group_by(treaty_id) %>%
  
  # rank the development periods
  mutate(r_yr=rank(dev_month_yr), r_qtr=rank(dev_month_qtr)) %>%
  
  # if you are rank 1, prior is 0, otherwise, prior is the dev month corresponding to the rank - 1 value
  mutate(prior_dev_month_yr=ifelse(r_yr==1, 0, lag(dev_month_yr))) %>%
  mutate(prior_dev_month_qtr=ifelse(r_yr==1, 0, lag(dev_month_qtr))) %>%

  # ungroup
  ungroup() %>%

  # create incremental paid loss column (paid loss - prior paid loss for the same treaty)
  group_by(treaty_id) %>%
  mutate(inc_paid_loss=paid_loss - lag(paid_loss)) %>%
  # and also for reported loss
  mutate(inc_reported_loss=reported_loss - lag(reported_loss)) %>%

  # if either of the two have NA values, replace with the cumulative amount
  mutate(inc_paid_loss=ifelse(is.na(inc_paid_loss), paid_loss, inc_paid_loss)) %>%
  mutate(inc_reported_loss=ifelse(is.na(inc_reported_loss), reported_loss, inc_reported_loss)) %>%

  # ungroup
  ungroup()

# export model_data and treaty_id_lookup to different tabs in an excel file
model_data %>% write_excel("model_data.xlsx", sheet="model_data")
treaty_id_lookup %>% write_excel("model_data.xlsx", sheet="treaty_id_lookup")


model_data %>% head

## build stan data
stan_data <- list(
    # dimension/length inputs
    N=model_data %>% nrow
  , N_treaties=model_data$treaty_id %>% max
  , N_treaty_periods=model_data$treaty_year %>% unique() %>% as.vector() %>% length()
  , N_development_periods=c(3:(model_data$dev_month_yr %>% max())) %>% length()
  
  # data inputs
  , treaty_period=model_data$treaty_year - min(model_data$treaty_year + 1) # re-index treaty year starting with 1
  , development_period=model_data$dev_month_yr/3 # reindex development month starting with 1
  , exposure = model_data$premium
  , treaty_id = model_data$treaty_id 
  , cumulative_paid_loss = model_data$paid_loss
  
  # prior parameters
  , prior_params=c()
  
)

# read in file from: O:\PARM\Corporate Actuarial\Reserving\Scripts\stan\cre_model\cre_model.stan
cre_model <- stan_model(file="cre_model.stan")