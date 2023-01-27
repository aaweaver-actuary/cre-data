functions{
    /**
      * @title Find the prior cumulative loss amount
      * @description Find the prior cumulative loss amount for a given treaty and development period. 
      *  Should return the cumulative loss from the same treaty, one development period prior.
      *  If the development period is 1, return 0.
      * @param n Integer number of rows in the data.
      * @param treaty_id A vector of the treaty ID.
      * @param dev_period A vector of the development period.
      * @param cum_loss A vector of cumulative losses.
      * @return A vector of the prior cumulative loss amount.
      * @examples
      * > prior_cum_loss(6, c(1, 1, 1, 2, 2, 2), c(1, 2, 3, 1, 2, 3), c(10, 20, 30, 40, 50, 60))
      * [1]  0 10 20  0 40 50
      */
   vector prior_cum_loss(int n, vector treaty_id, vector dev_period, vector cum_loss) {
      // initialize the vector to return
      vector[n] prior_cum_loss;

      // loop through the data and find the prior cumulative loss amount
      for (i in 1:n) {

         // if the development period is 1, return 0
         if (dev_period[i] == 1) {
            prior_cum_loss[i] = 0;
         } 
         
         // otherwise, find the prior cumulative loss amount by looping through the data again
         else {
            for (j in 1:n) {
               // checks that the treaty ID and development period are the same,
               // but the development period is one less
               if (treaty_id[i] == treaty_id[j] && dev_period[i] == dev_period[j] + 1) {
                  prior_cum_loss[i] = cum_loss[j];
               }
            }
         }
      }

      // return the vector of prior cumulative loss amounts
      return prior_cum_loss;
   }
      
   // similar function as prior cum loss, but this one finds the prior development period for each treaty
   // includes the same style of comments as above
   /**
      * @title Find the prior development period
      * @description Find the prior development period for a given treaty and development period. 
      *  Should return the development period from the same treaty, one development period prior.
      *  If the development period is 1, return 0.
      * @param n Integer number of rows in the data.
      * @param treaty_id A vector of the treaty ID.
      * @param dev_period A vector of the development period.
      * @return A vector of the prior development period.
      * @examples
      * > prior_dev_period(6, c(1, 1, 1, 2, 2, 2), c(1, 2, 3, 1, 2, 3))
      * [1] 0 1 2 0 1 2
      */
   vector prior_dev_period(int n, vector treaty_id, vector dev_period) {
      // initialize the vector to return
      vector[n] prior_dev_period;

      // loop through the data and find the prior development period
      for (i in 1:n) {

         // if the development period is 1, return 0
         if (dev_period[i] == 1) {
            prior_dev_period[i] = 0;
         } 

         // otherwise, find the prior development period by looping through the data again
         else {
            for (j in 1:n) {

               // checks that the treaty ID and development period are the same,
               // but the development period is one less
               if (treaty_id[i] == treaty_id[j] && dev_period[i] == dev_period[j] + 1) {

                  // if so, assign the prior development period to the vector
                  prior_dev_period[i] = dev_period[j];
               }
            }

            // when prior dev period was initialized, it was set to 0, so every 
            // cell will at least have a value of 0
         }
      }

      return prior_dev_period;
   }

   /**
      * @title Cumulative to incremental
      * @description Convert cumulative loss to incremental loss. This is done by subtracting
      * the cumulative loss from the previous cumulative loss, where previous means one
      * development period earlier. If the treaty is in the first development period, the
      * incremental loss is the same as the cumulative loss.
      * @param N The number of data points.
      * @param cum_loss A vector of length `N` with cumulative losses by treaty.
      * @param treaty_id An integer vector of length `N` with the treaty ID for each cumulative loss.
      * @return A vector of length `N` of incremental losses by treaty.
      * @examples
      * > cum_to_inc(5, c(10, 20, 30, 40, 50), c(1, 1, 1, 2, 2))
      * > // the first value is calculated as follows:
      * > // 10 - 0 = 10
      * > // the second value is calculated as follows:
      * > // 20 - 10 = 10
      * > // the third value is calculated as follows:
      * > // 30 - 20 = 10
      * > // the fourth value is calculated as follows:
      * > // 40 - 0 = 40
      * > // note that the fourth value is not 40 - 30 = 10, because the treaty ID is different
      * > // the fifth value is calculated as follows:
      * > // 50 - 40 = 10
      * [1] 10 10 10 40 10
      */
   vector cum_to_inc(int N, vector cum_loss, vector treaty_id) {
      // initialize a vector of length N to hold the incremental loss
      vector[N] inc_loss;

      // loop through the data
      for (n in 1:N) {

         if (n == 1) {
            // if the current treaty is in the first development period,
            // the incremental loss is the same as the cumulative loss
            inc_loss[n] = cum_loss[n];
         }

         else {
            // if the current treaty ID is the same as the previous one,
            if (treaty_id[n] == treaty_id[n-1]) {

               // subtract the previous cumulative loss from the current cumulative loss
               inc_loss[n] = cum_loss[n] - cum_loss[n-1];
            }
            
            // if the current treaty ID is not the same as the previous one,
            else {

               // the incremental loss is the same as the cumulative loss
               inc_loss[n] = cum_loss[n];
            }   
         }
         
      }

      // return the incremental loss
      return inc_loss;
   }

   // opposite of cum_to_inc -> incremental to cumulative
   /**
        * @title Incremental to cumulative
        * @description Convert incremental loss to cumulative loss. This is done by adding
        * the incremental loss to the previous cumulative loss, where previous means one
        * development period earlier. If the treaty is in the first development period, the
        * cumulative loss is the same as the incremental loss.
        * @param N The number of data points.
        * @param inc_loss A vector of length `N` with incremental losses by treaty.
        * @param treaty_id A vector of length `N` with treaty IDs for each treaty.
        * @return A vector of length `N` of cumulative losses by treaty.
        * @examples
        * > inc_to_cum(5, c(10, 10, 10, 40, 10), c(1, 1, 1, 2, 2))
        * > // the first value is calculated as follows:
        * > // 10 - 0 = 10
        * > // the second value is calculated as follows:
        * > // 10 + 10 = 20
        * > // the third value is calculated as follows:
        * > // 10 + 20 = 30
        * > // the fourth value is calculated as follows:
        * > // 40 - 0 = 40
        * > // note that the fourth value is not 40 + 30 = 70, because the treaty ID is different
        * > // the fifth value is calculated as follows:
        * > // 10 + 40 = 50
        * [1] 10 20 30 40 50
        */
    vector inc_to_cum(int N, vector inc_loss, vector treaty_id) {
        // initialize a vector of length N to hold the cumulative loss
        vector[N] cum_loss;
    
        // loop through the data
        for (n in 1:N) {
            if(n==1){
                // the cumulative loss is the same as the incremental loss
                cum_loss[n] = inc_loss[n];
                }
            else{
                // if the current treaty ID is the same as the previous one,
                if (treaty_id[n] == treaty_id[n-1]) {
                    
                    // add the previous cumulative loss to the current incremental loss
                    cum_loss[n] = inc_loss[n] + cum_loss[n-1];
                    }
                    
                    // if the current treaty ID is not the same as the previous one,
                else {
    
            // the cumulative loss is the same as the incremental loss
            cum_loss[n] = inc_loss[n];
                }
                }
        }
    
        // return the cumulative loss
        return cum_loss;
    }

    

   // N_treaty_periods x N_development_periods matrix of calendar periods, 
   // where each row is a treaty period and each column is a development period
   // and each cell contains the calendar period number
   /**
      * @title Calendar periods
      * @description Calculate the calendar periods for each treaty and development period.
      * @param N_treaty_periods The number of treaty periods.
      * @param N_development_periods The number of development periods.
      *        Should expect that `N_development_periods` = `N_treaty_periods` * 4.
      * @return A matrix of size `N_treaty_periods` x `N_development_periods` of calendar periods.
      * @examples
      * > calendar_periods(2, 8)
      * 1 2 3 4 5 6 7 8
      * 5 6 7 8 9 10 11 12
      * > # note that the first row is the same as the development periods, and the second row is the
      * > # development periods plus 4. from this pattern you can see that if there were a third row,
      * > # the calendar periods would be the development periods plus 8.
      * > calendar_periods(3, 12)
      * 1 2 3 4 5 6 7 8 9 10 11 12
      * 5 6 7 8 9 10 11 12 13 14 15 16
      * 9 10 11 12 13 14 15 16 17 18 19 20
      * > # this pattern continues for as many rows as there are treaty periods, and is because the
      * > # treaty periods are treaty years, while the development periods are development quarters (meaning
      * > # there are 4 development periods per treaty year)
      * > # if the treaties were given in quarters, then the calendar periods would be the development periods
      * > # in the first row, the development periods plus 1 in the second row, etc
      */
   matrix calendar_periods(int N_treaty_periods, int N_development_periods) {
      // initialize a matrix of size N_treaty_periods x N_development_periods to hold the calendar periods
      matrix[N_treaty_periods, N_development_periods] calendar_periods;
    
      // loop through the treaty periods
      for (treaty_period in 1:N_treaty_periods) {
         // loop through the development periods
         for (development_period in 1:N_development_periods) {
            // calculate the calendar period by adding the development period to 4 times the treaty period
            // minus 1 (because the treaty periods are treaty years, while the development periods are
            // development quarters (meaning there are 4 development periods per treaty year))
            // also note that treaty period starts at 1
            calendar_periods[treaty_period, development_period] = development_period + 4 * (treaty_period - 1);
         }
      }
    
      // return the calendar periods
      return calendar_periods;
   }

   /**
      * @title Calendar periods in treaty period-development period pair
      * @description Calculate a matrix of similar size as `calendar_periods`, but filled with 0s and 1s.
      * Begins by first calculating the calendar periods for each treaty and development period using the
      * `calendar_periods` function defined above. Then, for each treaty period-development period pair,
      * the function calculates whether the calendar period is in the treaty period-development period pair
      * given by the input vectors `treaty_period` and `development_period`. If the calendar period is in
      * the treaty period-development period pair, the function returns a 1, and if the calendar period is
      * not in the treaty period-development period pair, the function returns a 0. The function returns
      * a matrix of size `N_treaty_periods` x `N_development_periods` of 0s and 1s.
      * @param N_treaty_periods The number of treaty periods.
      * @param N_development_periods The number of development periods.
      * @param treaty_period A vector of length `N_treaty_periods` with treaty periods.
      * @param development_period A vector of length `N_development_periods` with development periods.
      * @return A matrix of size `N_treaty_periods` x `N_development_periods` of 0s and 1s.
      * @examples
      * > N_treaty_periods = 3
      * > N_development_periods = 12
      * > treaty_period = c(rep(1, 12)) %>% c(rep(2, 8)) %>% c(rep(3, 4))
      * > length(treaty_period)
      * [1] 24
      * > # this returns a vector of length 24 with the first 12 positions = 1, the next 8 positions = 2, and the last 4 positions = 3
      * > treaty_period
      * [1] 1 1 1 1 1 1 1 1 1 1 1 1 2 2 2 2 2 2 2 2 3 3 3 3
      * > development_period = c(1:12) %>% c(1:8) %>% c(1:4)
      * > length(development_period)
      * [1] 24
      * > # this returns a vector of length 24 with the first 12 positions = 1-12, the next 8 positions = 1-8, and the last 4 positions = 1-4
      * > development_period
      * [1] 1 2 3 4 5 6 7 8 9 10 11 12 1 2 3 4 5 6 7 8 1 2 3 4
      * > calendar_periods(N_treaty_periods, N_development_periods)
      * 1 2 3 4 5 6 7 8 9 10 11 12
      * 5 6 7 8 9 10 11 12 13 14 15 16
      * 9 10 11 12 13 14 15 16 17 18 19 20
      * > # this returns a matrix of size 3 x 12 with the first row = 1-12, the second row = 5-16, and the third row = 9-20

      * > # now we want to calculate whether each calendar period is in the treaty period-development period pair
      * > # not all calendar periods can be calculated from a treaty period-development period pair
      * > # the most recent calendar period is in the treaty period-development period pair with the max value of:
      * > # development_period + 4 * (treaty_period - 1)
      * > df = data.frame(t=treaty_period, d=development_period, adj_t = treaty_period - 1) %>%
      * +   mutate(x = d + 4 * adj_t)
      * > df
      *    t  d adj_t  x
      * 1  1  1     0  1
      * 2  1  2     0  2
      * 3  1  3     0  3
      * 4  1  4     0  4
      * 5  1  5     0  5
      * 6  1  6     0  6
      * 7  1  7     0  7
      * 8  1  8     0  8
      * 9  1  9     0  9
      * 10 1 10     0 10
      * 11 1 11     0 11
      * 12 1 12     0 12    # the first 12 calendar periods are in the treaty period-development period pair with treaty period = 1 and development period = 1-12
      * 13 2  1     1  5
      * 14 2  2     1  6
      * 15 2  3     1  7
      * 16 2  4     1  8
      * 17 2  5     1  9
      * 18 2  6     1 10
      * 19 2  7     1 11
      * 20 2  8     1 12    # the next 8 calendar periods are in the treaty period-development period pair with treaty period = 2 and development period = 1-8
      * 21 3  1     2  9
      * 22 3  2     2 10
      * 23 3  3     2 11
      * 24 3  4     2 12    # the last 4 calendar periods are in the treaty period-development period pair with treaty period = 3 and development period = 1-4

      * > df_max <- df[df$c==max(df$x), ]
      * > # we can check what this should be by scanning the df matrix and noticing that the max value 
      * > # of treaty period + development period - 1 is 12, and this more than once: once for treaty period = 1 and development period = 12,
      * > # and once for treaty period = 2 and development period = 8, and once for treaty period = 3 and development period = 4
      * > # so it seems this happens for each treaty period with the max value of development period for that treaty period
      * > df_max
      *    t  d adj_t  x c
      * 12 1 12     0 12 12
      * 20 2  8     1 12 12
      * 24 3  4     2 12 12

      * > # we can also check that the max value of treaty period + development period - 1 is 12 by using the max function:   
      * > max(df$x)
      * [1] 12

      * > # now we can calculate the matrix of 0s and 1s
      * > df %>%
      * +   mutate(in_treaty_period_development_period = ifelse(x <= max(df$x), 1, 0)) %>%
      * +   select(in_treaty_period_development_period) %>%
      * +   matrix(nrow = N_treaty_periods, ncol = N_development_periods)
      *      [,1] [,2] [,3] [,4] [,5] [,6] [,7] [,8] [,9] [,10] [,11] [,12]
      * [1,]    1    1    1    1    1    1    1    1    1     1     1     1
      * [2,]    1    1    1    1    1    1    1    1    0     0     0     0
      * [3,]    1    1    1    1    0    0    0    0    0     0     0     0
      * > # this returns a matrix of size 3 x 12 with the first row = 1-12, the second row = 5-16, and the third row = 9-20
      * > # the first row is all 1s because all calendar periods are in the treaty period-development period pair with treaty period = 1 and development period = 1-12
      * > # the second row is all 1s until development period = 8, and then all 0s because all calendar periods after development period = 8 are not in the treaty period-development period pair with treaty period = 2 and development period = 1-8
      * > # the third row is all 1s until development period = 4, and then all 0s because all calendar periods after development period = 4 are not in the treaty period-development period pair with treaty period = 3 and development period = 1-4
      */
   matrix calendar_period_indicator_matrix(int N_treaty_periods, int N_development_periods) {
      // create a vector of length N_treaty_periods * N_development_periods
      // with the first N_development_periods positions = development_period + (4 * (treaty_period[1] - 1))
      // the next N_development_periods positions = development_period + (4 * (treaty_period[2] - 1))
      // and so on
      vector[N_treaty_periods * N_development_periods] x;

      // create a matrix of 0s and 1s with 1s in the positions where the vector is less than or equal to the max value
      // and 0s in the positions where the vector is greater than the max value
      matrix[N_treaty_periods, N_development_periods] calendar_period_indicator_matrix;

      // calculate the max value of the vector
      int max_x = fmax(x);

      // loop over treaty periods and development periods
      for (t in 1:N_treaty_periods) {
         for (d in 1:N_development_periods) {

            // calculate the value of the vector at position (t, d)
            x[(t - 1) * N_development_periods + d] = d + 4 * (t - 1);
         }
      }

      // loop over treaty periods and development periods
      for (t in 1:N_treaty_periods) {
         for (d in 1:N_development_periods) {

            // calculate the value of the matrix at position (t, d)
            if (x[(t - 1) * N_development_periods + d] <= max_x) {
               calendar_period_indicator_matrix[t, d] = 1;
            } else {
               calendar_period_indicator_matrix[t, d] = 0;
            }
         }
      }

      // return the matrix
      
      return calendar_period_indicator_matrix;
   }    
}