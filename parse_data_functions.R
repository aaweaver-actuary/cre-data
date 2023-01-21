# the input is a 2-way lookup data frame with index columns: "lob", "group", "cre_id", "sap_id", "deal_name", "effective_date", "treaty_year", "exposure"
# and value columns starting at 2016Q1 and ending at 2021Q4 representing years and quarters, whose data is the paid loss for that year and quarter

# the goal is to reshape and clean the data so that it can be used for analysis in the "cre_model.stan" data block

# the output is a long, skinny table with columns:
# lob, model_gp, cinfin_id, sap_id, deal_name, eff_date, treaty_year, premium, cy, cm, paid_loss (paid loss is the value that fills the data frame)

# uses the data.table package and dtplyr notation

# replicates the effect of the following MS power query:
# let
#     Source = Excel.CurrentWorkbook(){[Name="dat"]}[Content],
#     #"Changed Type" = Table.TransformColumnTypes(Source,{{"Column1", type text}, {"Column2", type text}, {"Column3", type text}, {"Column4", type any}, {"Column5", type text}, {"Column6", type any}, {"Column7", type any}, {"Column8", type any}, {"Column9", type any}, {"Column10", type any}, {"Column11", type any}, {"Column12", type any}, {"Column13", type any}, {"Column14", type any}, {"Column15", type any}, {"Column16", type any}, {"Column17", type any}, {"Column18", type any}, {"Column19", type any}, {"Column20", type any}, {"Column21", type any}, {"Column22", type any}, {"Column23", type any}, {"Column24", type any}, {"Column25", type any}, {"Column26", type any}, {"Column27", type any}, {"Column28", type any}, {"Column29", type any}, {"Column30", type any}, {"Column31", type any}, {"Column32", type any}, {"Column33", type any}, {"Column34", type any}, {"Column35", type any}, {"Column36", type any}, {"Column37", type any}, {"Column38", type any}, {"Column39", type any}, {"Column40", type any}, {"Column41", type any}, {"Column42", type any}, {"Column43", type any}, {"Column44", type any}, {"Column45", type any}, {"Column46", type any}, {"Column47", type any}, {"Column48", type any}, {"Column49", type any}, {"Column50", type any}, {"Column51", type any}, {"Column52", type any}, {"Column53", type any}, {"Column54", type any}, {"Column55", type any}, {"Column56", type any}}),
#     #"Promoted Headers" = Table.PromoteHeaders(#"Changed Type", [PromoteAllScalars=true]),
#     #"Changed Type1" = Table.TransformColumnTypes(#"Promoted Headers",{{"LOB", type text}, {"For modeling", type text}, {"CinFin #", type text}, {"SAP #", Int64.Type}, {"Deal Name", type text}, {"Eff. Date", type datetime}, {"Treaty Year", Int64.Type}, {"Premium", type number}, {"2016.3.3", Int64.Type}, {"2016.6.3", Int64.Type}, {"2016.9.3", Int64.Type}, {"2016.12.31", Int64.Type}, {"2017.3.31", Int64.Type}, {"2017.6.3", Int64.Type}, {"2017.9.3", Int64.Type}, {"2017.12.31", Int64.Type}, {"2018.3.31", Int64.Type}, {"2018.6.3", type number}, {"2018.9.3", type number}, {"2018.12.31", type number}, {"2019.3.31", type number}, {"2019.6.3", type number}, {"2019.9.3", type number}, {"2019.12.31", type number}, {"2020.3.31", type number}, {"2020.6.3", type number}, {"2020.9.3", type number}, {"2020.12.31", type number}, {"2021.3.31", type number}, {"2021.6.3", type number}, {"2021.9.3", type number}, {"2021.12.31", type number}, {"2016.3.3_inc", Int64.Type}, {"2016.6.3_inc", Int64.Type}, {"2016.9.3_inc", Int64.Type}, {"2016.12.31_inc", Int64.Type}, {"2017.3.31_inc", Int64.Type}, {"2017.6.3_inc", Int64.Type}, {"2017.9.3_inc", Int64.Type}, {"2017.12.31_inc", Int64.Type}, {"2018.3.31_inc", Int64.Type}, {"2018.6.3_inc", type number}, {"2018.9.3_inc", type number}, {"2018.12.31_inc", type number}, {"2019.3.31_inc", type number}, {"2019.6.3_inc", type number}, {"2019.9.3_inc", type number}, {"2019.12.31_inc", type number}, {"2020.3.31_inc", type number}, {"2020.6.3_inc", type number}, {"2020.9.3_inc", type number}, {"2020.12.31_inc", type number}, {"2021.3.31_inc", type number}, {"2021.6.3_inc", type number}, {"2021.9.3_inc", type number}, {"2021.12.31_inc", type number}}),
#     #"Removed Columns" = Table.RemoveColumns(#"Changed Type1",{"2016.6.3", "2016.9.3", "2016.12.31", "2017.3.31", "2017.6.3", "2017.9.3", "2017.12.31", "2018.3.31", "2018.6.3", "2018.9.3", "2018.12.31", "2019.3.31", "2019.6.3", "2019.9.3", "2019.12.31", "2020.3.31", "2020.6.3", "2020.9.3", "2020.12.31", "2021.3.31", "2021.6.3", "2021.9.3", "2021.12.31"}),
#     #"Unpivoted Columns" = Table.UnpivotOtherColumns(#"Removed Columns", {"LOB", "For modeling", "CinFin #", "SAP #", "Deal Name", "Eff. Date", "Treaty Year", "Premium", "2016.3.3"}, "Attribute", "Value"),
#     #"Split Column by Delimiter" = Table.SplitColumn(#"Unpivoted Columns", "Attribute", Splitter.SplitTextByDelimiter("_", QuoteStyle.Csv), {"Attribute.1", "Attribute.2"}),
#     #"Changed Type2" = Table.TransformColumnTypes(#"Split Column by Delimiter",{{"Attribute.1", type text}, {"Attribute.2", type text}}),
#     #"Split Column by Delimiter1" = Table.SplitColumn(#"Changed Type2", "Attribute.1", Splitter.SplitTextByDelimiter(".", QuoteStyle.Csv), {"Attribute.1.1", "Attribute.1.2", "Attribute.1.3"}),
#     #"Removed Columns2" = Table.RemoveColumns(#"Split Column by Delimiter1",{"Attribute.1.3"}),
#     #"Removed Columns1" = Table.RemoveColumns(#"Removed Columns2",{"Attribute.2"}),
#     #"Renamed Columns" = Table.RenameColumns(#"Removed Columns1",{{"Value", "paid_loss"}, {"Attribute.1.2", "cm"}, {"Attribute.1.1", "cy"}}),
#     #"Renamed Columns1" = Table.RenameColumns(#"Removed Columns3",{{"LOB", "lob"}, {"For modeling", "model_gp"}, {"CinFin #", "cinfin_id"}, {"SAP #", "sap_id"}, {"Deal Name", "deal_name"}, {"Eff. Date", "eff_date"}, {"Treaty Year", "treaty_year"}, {"Premium", "premium"}})
# in
#     #"Renamed Columns1"

# libraries
library(tidyverse)
library(lubridate)
library(data.table)
library(dplyr)

# function that reads in data from an excel workbook and returns a data.table
# add in extremely detailed comments in roxygen2 format:

#' Read in data from an excel workbook
#' 
#' @param file_path path to the excel workbook
#' @param sheet_name name of the sheet in the workbook to read in
#' @return a data.table
#' @export
#' @examples
#' read_data("data.xlsx", "Sheet1")
#' @importFrom readxl read_excel
#' @importFrom data.table as.data.table
#' @importFrom dplyr select, rename, mutate_at, vars, starts_with
read_data <- function(file_path, sheet_name) {
  # read in data
  data <- read_excel(file_path, sheet = sheet_name)
  
  # convert to data.table
  data <- as.data.table(data)
  
  # return data
  return(data)
}

# function that implements the step-by-step process for cleaning the data
# outlined in the Power Query script above
#' Clean data
#' 
#' @description This function implements the step-by-step process for
#' cleaning the data outlined in the Power Query script above
#' This function:
#' 1. unpivots columns starting with 20xx, with headers put in a column called Attribute.1
#' 2. splits column by `date_delim` and put the results in columns called Attribute.1.1, Attribute.1.2, and Attribute.1.3
#' 3. removes day column
#' 4. renames columns
#' 5. converts columns to appropriate data types
#' 6. adds in development period column where dev prd = 12*(cy - treaty_year) + cm
#' @param datatable a data.table
#' @param date_delim the delimiter used in the date column
#'        (default = ".")
#' @return a data.table
#' @export
#' @examples
#' > # assume data has lobs A, B, C, groups 1, 2, 3, and 4, cinfin ids 1-20, sap ids 1-20 as well
#' > # assume data has deal names "Deal [cinfin id]", effective dates all 1/1/2020, treaty years all 2020, premiums all 1000
#' > # This will return a well-structured and formatted data.table with 5 rows and 11 columns
#' > clean_data(data) %>% head(5) %>% View
#' # A tibble: 5 x 11
#'  lob model_gp cinfin_id sap_id deal_name eff_date treaty_year premium cy cm paid_loss
#' <chr> <chr>      <dbl>  <dbl> <chr>     <date>        <dbl>   <dbl> <dbl> <dbl>     <dbl>
#' 1 A     1             1      1 Deal 1   2020-01-01      2020    1000  2020   1       100
#' 2 A     1             1      1 Deal 1   2020-01-01      2020    1000  2020   2       200
#' 3 A     1             1      1 Deal 1   2020-01-01      2020    1000  2020   3       300
#' 4 A     1             1      1 Deal 1   2020-01-01      2020    1000  2020   4       400
#' 5 A     1             1      1 Deal 1   2020-01-01      2020    1000  2020   5       500
#' # ... with 1 more variable: dev_prd <dbl>    
#' 
#'  
#' 
clean_data <- function(datatable, date_delim="."){
    
    datatable <- datatable %>% 
        # unpivot columns starting with 20xx, with headers put in a column called Attribute.1 
        unpivot(cols = starts_with("20"), names_to = "Attribute.1") %>%
    
        # split column by `date_delim` and put the results in columns called Attribute.1.1, Attribute.1.2, and Attribute.1.3``
        separate(Attribute.1, into = c("Attribute.1.1", "Attribute.1.2", "Attribute.1.3"), sep = date_delim) %>%

        # remove day column
        select(-Attribute.1.3) %>%    

        # rename columns
        rename(paid_loss = Value, cm = Attribute.1.2, cy = Attribute.1.1) %>%

        # rename more columns
        rename(lob = LOB, model_gp = `For modeling`
        , cinfin_id = `CinFin #`, sap_id = `SAP #`, deal_name = `Deal Name`
        , eff_date = `Eff. Date`, treaty_year = `Treaty Year`, premium = Premium) %>%

        # convert columns to appropriate data types
        mutate_at(vars(cy, cm, paid_loss, premium), as.numeric) %>%
        mutate_at(vars(eff_date), as.Date)

        # add in development period column where dev prd = 12*(cy - treaty_year) + cm
        datatable$dev_prd <- 12*(datatable$cy - datatable$treaty_year) + datatable$cm

    return(datatable)
}

# function that takes in a data.table and returns a list of data elements needed for `cre_model.stan`
# this is the data block:
# data {
#    // number of data points
#    int<lower=1> N;
   
#    // number of treaties in data
#    int<lower=1> N_treaties;

#    // number of distinct treaty periods
#    int<lower=1> N_treaty_periods;

#    // number of distinct development periods
#    int<lower=1> N_development_periods;

#    // treaty period
#    vector<lower=1, upper=N_treaty_period>[N] treaty_period;

#    // development period
#    vector<lower=1, upper=N_development_periods>[N] development_period;

#    // estimated exposure for each treaty
#    vector[<lower=0>N] exposure;

#    // treaty id for each data point
#    vector<lower=1, upper=N_treaties>[N] treaty_id;

#    // paid loss for each treaty period - development period pair
#    vector[N] cumulative_paid_loss;

#    // reported loss for each treaty period - dev period
#    // vector[N] cumulative_reported_loss;

#    // vector of prior estimates of the warp, theta, and sigma parameters
#    // (in that order) for the cumulative paid loss
#    vector[3] prior_params;
# }
prep_data <- function(datatable, prior_params=c(1,1,1)){
    # create a list of data elements needed for `cre_model.stan`
    data_list <- list(
        N = nrow(datatable)
        , N_treaties = length(unique(datatable$cinfin_id))
        , N_treaty_periods = length(unique(datatable$treaty_year))
        , N_development_periods = length(unique(datatable$dev_prd))
        , treaty_period = datatable$treaty_year
        , development_period = datatable$dev_prd
        , exposure = datatable$premium
        , treaty_id = datatable$cinfin_id
        , cumulative_paid_loss = datatable$paid_loss
        , prior_params = prior_params
    )
    
    return(data_list)
}