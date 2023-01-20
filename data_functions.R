m2q <- function(x){
  if(x==1) out=1
  else if(x==2) out=1
  else if(x==3) out=1
  else if(x==4) out=2
  else if(x==5) out=2
  else if(x==6) out=2
  else if(x==7) out=3
  else if(x==8) out=3
  else if(x==9) out=3
  else if(x==10) out=4
  else if(x==11) out=4
  else if(x==12) out=4
  else out=0
  return(out)
}

get_data <- function(df, model_group){
  df1 <- df %>% filter(model_gp==model_group)
  
  lob_id <- df1$lob
  
  treaty_id <- df1$treaty_id
}