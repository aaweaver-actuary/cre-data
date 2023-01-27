#include "clark_model_functions.stan"
#include "data_manipulation_functions.stan"


functions {
   

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

   // matrix of similar size as calendar_periods, but filled with 0s and 1s
   // where 1s indicate that the calendar period is in the treaty period-
   // development period pair given by the input vectors treaty_period and
   // development_period, and 0s indicate that the calendar period is not
   // in the treaty period-development period pair given by the input vectors
   // treaty_period and development_period
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
      // this function returns a matrix of 0s and 1s indicating whether each calendar period is in the treaty period-development period pair
      // the matrix has N_treaty_periods rows and N_development_periods columns
      // the matrix is calculated by first creating a vector of length N_treaty_periods * N_development_periods
      // with the first N_development_periods positions = development_period + (4 * (treaty_period[1] - 1))
      // the next N_development_periods positions = development_period + (4 * (treaty_period[2] - 1))
      // and so on
      // then we calculate the max value of this vector
      // and then we create a matrix of 0s and 1s with 1s in the positions where the vector is less than or equal to the max value
      // and 0s in the positions where the vector is greater than the max value
      // the matrix is returned
      // the matrix is used to calculate the calendar period indicator vector

      // create a vector of length N_treaty_periods * N_development_periods
      // with the first N_development_periods positions = development_period + (4 * (treaty_period[1] - 1))
      // the next N_development_periods positions = development_period + (4 * (treaty_period[2] - 1))
      // and so on
      vector[N_treaty_periods * N_development_periods] x;

      // loop over treaty periods and development periods
      for (t in 1:N_treaty_periods) {
         for (d in 1:N_development_periods) {

            // calculate the value of the vector at position (t, d)
            x[(t - 1) * N_development_periods + d] = d + 4 * (t - 1);
         }
      }

      // calculate the max value of the vector
      int max_x = max(x);

      // create a matrix of 0s and 1s with 1s in the positions where the vector is less than or equal to the max value
      // and 0s in the positions where the vector is greater than the max value
      matrix[N_treaty_periods, N_development_periods] calendar_period_indicator_matrix;

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
