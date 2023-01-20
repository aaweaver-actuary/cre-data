library(dplyr)
library(readxl)
library(lubridate)

rawdat <- read_excel("./Data for Andy 4q21 v1.xlsx", "model_data")

df <- rawdat

treaty_df <- df %>% select(lob, model_gp, cinfin_id, sap_id, deal_name) %>% unique() %>%
  arrange(model_gp, lob, cinfin_id, sap_id, deal_name) %>%
  mutate(treaty_id=row_number()) %>%
  select(treaty_id, model_gp, lob, cinfin_id, sap_id, deal_name)

df1 <- df %>%
  left_join(treaty_df, by=c('model_gp', 'lob', 'cinfin_id', 'sap_id', 'deal_name')) %>%
  select(-c('cinfin_id', 'deal_name', 'sap_id')) %>%
  mutate(treaty_month=month(eff_date)) 

df1$cy <- as.numeric(df1$cy)
df1$cm <- as.numeric(df1$cm)

df1 <- df1 %>%
  mutate(treaty_quarter=df1$treaty_month %>% sapply(m2q)) %>%
  mutate(cq=df1$cm %>% sapply(m2q))

df1 <- df1 %>%
  mutate(treaty_year_dev_month=12*(df1$cy - df1$treaty_year + 1)) %>%
  mutate(treaty_qtr_dev_month=12*(df1$cy - df1$treaty_year) + (df1$cm - (4 * df1$treaty_quarter)+3)) %>%
  mutate(treaty_month_dev_month=12*(df1$cy - df1$treaty_year) + (df1$cm - df1$treaty_month + 1)) %>%
  select(model_gp, lob, treaty_id, treaty_year, treaty_quarter, treaty_month, cy, cm, treaty_year_dev_month, treaty_qtr_dev_month, treaty_month_dev_month, paid_loss, premium)

cas_pr_df <- df1 %>% filter(model_gp=="Casualty Proportional")
short_tail_df <- df1 %>% filter(model_gp=="Short Tail Reinsurance")
cas_xs_df <- df1 %>% filter(model_gp=="XS Casualty")
trans_df <- df1 %>% filter(model_gp=="Transactional")


get

