# the input is a 2-way lookup data frame with index columns: "lob", "group", "cre_id", "sap_id", "deal_name", "effective_date", "treaty_year", "exposure"
# and value columns starting at 2016Q1 and ending at 2021Q4 representing years and quarters, whose data is the paid loss for that year and quarter

# the goal is to reshape and clean the data so that it can be used for analysis in the "cre_model.stan" data block

# the output is a long, skinny table with columns:
# lob, model_gp, cinfin_id, sap_id, deal_name, eff_date, treaty_year, premium, cy, cm, paid_loss (paid loss is the value that fills the data frame)

