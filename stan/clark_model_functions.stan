   /** 
      * @title Prior age lookup
      * @description This function looks up the value corresponding to the prior age for a given age and group.
      * The prior age is the age that immediately precedes the given age. If the given age is the first age in
      * the development period, the prior age is the first age in the development period. If the given age is
      * the first age in the development period for a given group, the prior age is the first age in the development
      * period for that group. If the given age is the first age in the development period for a given group, and
      * the first age in the development period for that group is the first age in the development period, the
      * prior age is the first age in the development period. If the groups are not the same, the prior age is
      * the first age in the development period for that group.
      * @param n Integer number of rows in the data.
      * @param dev_age A vector of development ages.
      * @param gp A vector of group numbers. This is used to calculate the prior age by group. Only look up the
      * prior age if the group number is the same.
      * @param x The vector of values to look up the prior value for.
      * @return A vector of prior values.
      * @examples
      * > n=10
      * > dev_age=(1,2,3,4,1,2,3,1,2,1)
      * > gp=(1,1,1,1,2,2,2,3,3,4)
      * > x=(1,2,3,4,5,6,7,8,9,10)
      * > data.frame(gp=gp, dev_age=dev_age, x=x, prior_x=prior_value(n, dev_age, gp, x))
      *     gp    dev_age  x  prior_x
      * 1   1     1        1  0
      * 2   1     2        2  1
      * 3   1     3        3  2
      * 4   1     4        4  3
      * 5   2     1        5  0
      * 6   2     2        6  5
      * 7   2     3        7  6
      * 8   3     1        8  0
      * 9   3     2        9  8
      * 10  4     1       10  0
      * note that in rows 1, 5, and 8, the age is the first age in the development period, so the prior value is 0
      * which indicates that there is no prior value for that age
      */
   vector prior_value(int n, vector dev_age, vector gp, vector x) {
      // initialize the vector of prior values (sorted and original order)
      vector[n] out;
      vector[n] out_sorted;

      // capture the current order of the data
      vector[n] cur_order = 1:n;

      // sort the data by group number and development age (ascending) so
      // that the prior value can be calculated by group and age in a loop
      vector[n] sorted_order = sort_indices_2d(gp, dev_age);
      vector[n] sorted_dev_age = dev_age[sorted_order];
      vector[n] sorted_gp = gp[sorted_order];
      vector[n] sorted_x = x[sorted_order];

      // loop through the data and calculate the prior value
      for(i in 1:n){
         
         // if the age is the first age in the data, the prior value is 0
         if(sorted_dev_age[i] == 1){
            out_sorted[i] = 0;
         }
         
         // if the group number is the same as the previous age, look up the value at the previous age
         else if(sorted_gp[i] == sorted_gp[i-1]){
            out_sorted[i] = sorted_x[i-1];
         } 
         
         // otherwise, it is not the first row in the data, and the group number
         // is not the same as the previous age, so the prior value is 0
         // indicating that there is no prior value for that age
         else{
            out_sorted[i] = 0;
         }
      }

      // return the prior value in the original order of the data
      out = out_sorted[cur_order];
      return out;
   }
   
   /**
      * @title Cumulative Loss Calculation
      * @description Calculate the cumulative loss by group and age. This is the cumulative loss
      * for a given age, calculated as the sum of the incremental losses up to that age. The first age
      * in the development period is assumed to be `1`, and the cumulative loss for that age is simply
      * the incremental loss at that age. The cumulative loss for the second age is the sum of the
      * incremental loss at that age and the cumulative loss at the first age. The cumulative loss for    
      * the third age is the sum of the incremental loss at that age and the cumulative loss at the
      * second age, and so on.
      * @param n Integer number of rows in the data.
      * @param dev_age A vector of development ages.
      * @param gp A vector of group numbers. This is used to calculate the cumulative loss by group. Only add
      * the incremental loss at the previous age if the group number is the same.
      * @param inc A vector of incremental whatevers.
      * @return A vector of cumulative losses.
      * @examples
      * > cum_loss(10, (1,2,3,4,1,2,3,1,2,1), (1,1,1,1,2,2,2,3,3,4), (1,3,5,7,9,11,13,15,17,19))
      * [1]  1  4  9 16 25 36 49 64 81 100
      * see the example for the `inc_loss` function for an explanation of the results
      */
   vector cum_loss(int n, vector dev_age, vector gp, vector inc) {
      // initialize the vector of cumulative losses (sorted and original order)
      vector[n] out;
      vector[n] out_sorted;

      // capture the current order of the data
      vector[n] cur_order = 1:n;

      // sort the data by group number and development age (ascending) so
      // that the cumulative loss can be calculated by group and age in a loop
      vector[n] sorted_order = sort_indices_2d(gp, dev_age);
      vector[n] sorted_dev_age = dev_age[sorted_order];
      vector[n] sorted_gp = gp[sorted_order];
      vector[n] sorted_inc = inc[sorted_order];

      // loop through the data and calculate the cumulative loss
      for(i in 1:n){
         
         // the first age in the development period is assumed to be 1, and the cumulative loss for that age
         // is simply the incremental loss at that age
         if(i==1){   
            out_sorted[i] = sorted_inc[i];
         }
         
         // if the group number is the same as the previous age, add the incremental loss at the previous age
         // to the incremental loss at the current age
         else if(sorted_gp[i] == sorted_gp[i-1]){
            out_sorted[i] = sorted_inc[i] + out_sorted[i-1];
         } 
         
         // otherwise, just use the incremental loss at the current age
         else{
            out_sorted[i] = sorted_inc[i];
         }
      }

      // return the cumulative loss in the original order of the data
      out = out_sorted[cur_order];
      return out;
   }
  
  
  /**
      * @title Incremental Loss Calculation
      * @description Calculate the incremental loss by group and age. This is the incremental loss
      * for a given age, calculated as the difference between the cumulative loss at that age and the
      * cumulative loss at the previous age. The first age in the development period is assumed to be
      * `1`, and the incremental loss for that age is simply the cumulative loss at that age. The incremental
      * loss for the second age is the difference between the cumulative loss at that age and the cumulative
      * loss at the first age. The incremental loss for the third age is the difference between the cumulative
      * loss at that age and the cumulative loss at the second age, and so on.
      * @param n Integer number of rows in the data.
      * @param dev_age A vector of development ages.
      * @param gp A vector of group numbers. This is used to calculate the incremental loss by group. Only subtract
      * the cumulative loss at the previous age if the group number is the same.
      * @param cum A vector of cumulative whatevers.
      * @return A vector of incremental losses.
      * @examples
      * > inc_loss(10, (1,2,3,4,1,2,3,1,2,1), (1,1,1,1,2,2,2,3,3,4), (1,4,9,16,25,36,49,64,81,100))
      * [1]  1  3  5  7  9 11 13 15 17 19
      * > # for example, the first value is 1, because the cumulative loss at age 1 is 1, and there are no
      * > # previous ages to subtract from. The second value is 3, because the cumulative loss at age 2 is 4,
      * > # and the cumulative loss at age 1 is 1, AND the group number is the same (1). The third value is 5,
      * > # because the cumulative loss at age 3 is 9, and the cumulative loss at age 2 is 4, AND the group
      * > # number is the same (1). The fifth value is 25, because the cumulative loss at age 1 for group 2 is 25,
      * > # and there are no previous ages to subtract from in that group.
      */
   vector inc_loss(int n, vector dev_age, vector gp, vector cum) {
      // initialize the vector of incremental losses (sorted and original order)
      vector[n] out;
      vector[n] out_sorted;

      // capture the current order of the data
      vector[n] cur_order = 1:n;

      // sort the data by group number and development age (ascending) so
      // that the incremental loss can be calculated by group and age in a loop
      vector[n] sorted_order = sort_indices_2d(gp, dev_age);
      vector[n] sorted_dev_age = dev_age[sorted_order];
      vector[n] sorted_gp = gp[sorted_order];
      vector[n] sorted_cum = cum[sorted_order];


      // loop through the data and calculate the incremental loss
      for(i in 1:n){
         
         // the first age in the development period is assumed to be 1, and the incremental loss for that age
         // is simply the cumulative loss at that age
         if(i==1){   
            out_sorted[i] = sorted_cum[i];
         }
         
         // if the group number is the same as the previous age, subtract the cumulative loss at the previous age
         // from the cumulative loss at the current age
         else if(sorted_gp[i] == sorted_gp[i-1]){
            out_sorted[i] = sorted_cum[i] - sorted_cum[i-1];
         } 
         
         // otherwise, just use the cumulative loss at the current age
         else {
            out_sorted[i] = sorted_cum[i];
         }
      }

      // reorder the incremental losses to match the original order of the data
      for(i in 1:n){
         out[sorted_order[i]] = out_sorted[i];
      }

      // return the vector of incremental losses (original order)
      return out;
   }
  
  /**
      * @title Log-logistic distribution
      * @description The log-logistic distribution is a continuous probability distribution with parameters
      * `warp` and `theta`. This is the parameterization from Clark (2004).
      * @param n Integer number of rows in the data.
      * @param x A vector of values at which to evaluate the log-logistic distribution.
      * @param warp A real number that controls the shape of the distribution.
      * @param theta A real number that controls the scale of the distribution.
      * @return A vector of values of the log-logistic distribution at the values specified by \code{x}.
      * @references \url{https://en.wikipedia.org/wiki/Log-logistic_distribution}
      * @references Clark, David. (2004)
      * @examples
      * > G_loglogistic(1:10, 1, 1)
      * > // for example, the final value is 0.37142857, calculated as follows:
      * > // 10^1 / (10^1 + 1^1) = 0.9090909 / (0.9090909 + 1) = 0.9090909 / 1.9090909 = 0.37142857
      * [1] 0.09090909 0.11111111 0.13333333 0.15789474 0.18518519 0.21538462 0.24878049 0.28571429 0.32653061 0.37142857
      */
   vector G_loglogistic(int n, vector x, real warp, real theta) {
      vector[n] out;
      
      // loop through the data and calculate the log-logistic distribution
      for(i in 1:n){
         // calculate the log-logistic distribution
         out[i] = (x[i] ^ warp) / ((x[i] ^ warp) + (theta ^ warp)) ;
         }
      
      // return the vector of log-logistic distribution values
      return out;
   }

   /**
      * @title Weibull distribution function (`G`)
      * @description The Weibull distribution is a continuous probability distribution with parameters
      * `warp` and `theta`. This is the parameterization from Clark (2004), namely
      * `G(x) = 1 - exp( -(x/theta)^warp )`
      * @param `n` Integer number of rows in the data.
      * @param `x` A vector of values at which to evaluate the Weibull distribution.
      * @param `warp` A real number that controls the shape of the distribution.
      * @param `theta` A real number that controls the scale of the distribution.
      * @return A vector of values of the Weibull distribution at the values specified by `x`.
      * @references \url{https://en.wikipedia.org/wiki/Weibull_distribution}
      * @references Clark, David. (2004)
      * @examples
      * > G_weibull(1:10, 0.1, 10)
      * # (0.548, 0.573, 0.588, 0.598, 0.607, 0.613, 0.619, 0.624, 0.628, 0.632)
      * > // for example, the second value is calculated as follows:
      * > // 1 - exp( -(1/10)^0.1 ) = 1 - exp( -(0.1 ^ 0.1) ) = 1 - exp( -0.7943 ) = 0.573
      */
   vector G_weibull(int n, vector x, real warp, real theta) {
      vector[n] out;
      
      // loop through the data and calculate the Weibull distribution
      for(i in 1:n){
         // calculate the Weibull distribution
         out[i] = 1 - exp( -(x[i]/theta) ^ warp );
         }
      
      // return the vector of Weibull distribution values
      return out;
   }

   /**
      * @title General ELR Calculation
      * @description Use an arbitrary payment pattern `G` (not necessarily from the function above),
      * as well as loss data and exposure data, to calculate the ELR using the Cape Cod formula:
      * `ELR(x) = \sum \text{incremental loss} / \sum \text{(cum. exposure)} * (G(x) - G(x-1))`
      * where the `G` function is the arbitrary payment pattern, and the age `x`
      * is the most recent age in the development period for the specific treaty. `x-1` is the age
      * immediately preceding `x`, which may not necessarily be the same as `x-1` in the data. For example,
      * if the most recent age in the development period is 24, but the development periods are based on a
      * full year, then the age immediately preceding 24 is 12, not 23. This is because the development
      * periods are based on calendar years, not on the age of the policyholder. 
      * If the current age is the minimum age in the development period, then the age immediately preceding
      * `x` is `0` which is never in the data. In this case, `G(0)` is assumed to be `0`, and `G(x) - G(x-1)`
      * is simply `G(x)`.
      * @param n Integer number of rows in the data.
      * @param cum_loss A vector of cumulative losses. (Will need to convert to incremental losses.)
      * @param cum_exposure A vector of cumulative exposures.
      * @param x A vector of values at which to evaluate the payment pattern. These values are the development ages.
      * @param gp A vector identifying the cohort to which each row of the data belongs, used to calculate the 
      * incremental loss at each development age. The values in this vector should be integers, starting at 1.
      * Should typically expect this to refer to `accident_year`.
      * @param G A vector of values of the payment pattern at the values specified by `x`.
      * @return The ELR for the given payment pattern, loss data, and exposure data.
      * @examples
      * > G = (0.25, 0.5, 0.75, 1)
      * > n = 10
      * > gp = (1, 1, 1, 1, 2, 2, 2, 3, 3, 4)
      * > x = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
      * > cum_loss = (100, 200, 300, 400, 500, 650, 800, 900, 1000, 1200)
      * > cum_exposure = (10000, 10000, 10000, 10000, 50000, 50000, 50000, 80000, 80000, 100000)
      * > ELR(n, cum_loss, cum_exposure, x, gp, G)
      * > # incr_loss = (100, 100, 100, 100, 500, 150, 800, 100, 100, 1200)
      * > # note that the 5th incremental loss is 500, not 150, because the 5th row of the data
      * > # is in a different cohort (gp = 2) than the 4th row (gp = 1).
      * > # the first value is calculated as follows:
      * > # numerator = sum(incr_loss) = 100 + 100 + 100 + 100 + 500 + 150 + 800 + 100 + 100 + 1200 = 3000
      * > # denominator = sum[cum_exposure(x) * (G(x) - G(x-1))] = 
      * > # (10000 * (0.25 - 0)) + (10000 * (0.5 - 0.25)) + (10000 * (0.75 - 0.5)) + (10000 * (1 - 0.75)) +
      * > # (50000 * (0.25 - 0)) + (50000 * (0.5 - 0.25)) + (50000 * (0.75 - 0.5)) +
      * > # (80000 * (0.25 - 0)) + (80000 * (0.5 - 0.25)) +
      * > # (100000 * (0.25 - 0)) =
      * > # 2500 + 2500 + 2500 + 2500 +
      * > # 12500 + 12500 + 12500 +
      * > # 20000 + 20000 +
      * > # 25000 = 
      * > # 10000 + 37500 + 40000 + 25000 = 112500
      * > # ELR = 3000 / 112500 = 0.0266
      */
   real ELR(int n, vector cum_loss, vector cum_exposure, vector x, vector gp, vector G) {
      // convert cumulative loss to incremental loss
      vector[n] incr_loss;
      vector[n] sorted_incr_loss;

      // initialize the ELR, which is the output
      real ELR;

      // initialize the numerator of the ELR, which is the sum of the incremental loss
      real numerator = 0;

      // initialize the denominator of the ELR, which is the sum of the cumulative exposure
      // times the difference between the payment pattern at the current age and the payment
      // pattern at the previous age
      real denominator = 0;

      // store the current order of the data as the row number of the input data
      vector[n] cur_order = 1:n;

      // sort the data by gp and x
      vector[n] sorted_cum_loss = cum_loss[order(gp, x)];
      vector[n] sorted_cum_exposure = cum_exposure[order(gp, x)];
      vector[n] sorted_gp = gp[order(gp, x)];
      vector[n] sorted_x = x[order(gp, x)];
      vector[n] sorted_order = cur_order[order(gp, x)];
      
      // initialize the first value of incr_loss
      sorted_incr_loss[1] = sorted_cum_loss[1];

      // calculate the incremental loss
      for (i in 2:n) {
         if (sorted_gp[i] == sorted_gp[i-1]) {
            sorted_incr_loss[i] = sorted_cum_loss[i] - sorted_cum_loss[i-1];
         } else {
            sorted_incr_loss[i] = sorted_cum_loss[i];
         }
      }

      // calculate the numerator
      numerator = sum(sorted_incr_loss);

      // calculate the denominator
      for (i in 1:n) {
         // if the current age is 1, then the payment pattern is just G[1], so add the cumulative exposure
         // times G[1] to the denominator
         if (sorted_x[i] == 1) {
            denominator = denominator + sorted_cum_exposure[i] * G[1];
         } 
         
         // if the current age is not 1 and this is not the first row, then the payment pattern is
         // G[x] - G[x-1], so add the cumulative exposure
         else {
            denominator = denominator + sorted_cum_exposure[i] * (G[sorted_x[i]] - G[sorted_x[i] - 1]);
         }
      }

      // calculate the ELR
      ELR = numerator / denominator;

      return ELR;
   }
      
   /**
      * @title Calculation of ELR for the log-logistic cumulative distribution function.
      * @description Uses the `ELR` function and the `G_loglogistic` function to calculate the
      * ELR for the log-logistic cumulative distribution function. Will require all the parameters
      * that are required for the `ELR` function, as well as the parameters for the `G_loglogistic`
      * function.
      * @param n The number of rows in the data.
      * @param cum_loss A vector of cumulative losses by treaty.
      * @param cum_exposure A vector of cumulative exposures by treaty.
      * @param x A vector of ages.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param warp The warp parameter for the log-logistic cumulative distribution function.
      * @param theta The theta parameter for the log-logistic cumulative distribution function.
      * @return The ELR for the log-logistic cumulative distribution function.
      */
   real ELR_loglogistic(int n, vector cum_loss, vector cum_exposure, vector x, vector gp, real warp, real theta) {
      // calculate the payment pattern
      vector[n] G = G_loglogistic(n, x, warp, theta);

      // calculate the ELR
      real ELR = ELR(n, cum_loss, cum_exposure, x, gp, G);

      // return the ELR
      return ELR;
   }

   // function that takes the group, age, and cumulative loss and returns the cumulative loss for each
   // group that corresponds to the maximum age observed for that group
   /**
      * @title Calculation of current cumulative loss by group.
      * @description Use the group, age, and cumulative loss to calculate the maximum age cumulative
      * loss for each group. Will require the number of cohorts, the cumulative losses, the cohort
      * index, and the ages. For each group, cumulative loss that corresponds to the maximum age
      * observed for that group will be returned.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param cum_loss A vector of cumulative losses by treaty.
      * @param gp A vector of groups. Each group is a different cohort.
      * @param x A vector of ages.
      * @return A vector of maximum age cumulative loss.
      * @examples
      * > cum_loss_by_gp(6, 3, c(100, 200, 300, 400, 500, 600), c(1, 1, 1, 2, 2, 3), c(1, 2, 3, 1, 2, 1))
      * > # note that the output is a vector of length 3, not 6, because there are only 3 groups
      * > # note also that the output is sorted by group, not by age
      * > # maximum age for group 1 is 3, so the output for group 1 is 300
      * > # maximum age for group 2 is 2, so the output for group 2 is 500
      * > # maximum age for group 3 is 1, so the output for group 3 is 600
      * [1] 300 500 600
      */
   vector cum_loss_by_gp(int n, int n_gp, vector cum_loss, int[] gp, vector x) {
      // initialize the vector of maximum age cumulative loss
      vector[n_gp] max_age_cum_loss;
      int max_age = 0;

      // loop through the groups
      for (i in 1:n_gp) {
         // initialize the maximum age for the current group
         max_age = 0;         

         // loop through the ages
         for (j in 1:n) {

            // if the current group is equal to the current group in the loop, then check the age
            if (gp[j] == i) {

               // if the current age is greater than the current maximum age, then update the maximum age
               if (x[j] > max_age) {
                  max_age = x[j];
               }
            }
         }

         // loop through the ages again to find the cumulative loss that corresponds to the maximum age
         // we found in the previous loop
         for (j in 1:n) {

            // if the current group is equal to the current group in the loop, then check the age
            if (gp[j] == i) {

               // if the current age is equal to the maximum age, then update the maximum age cumulative loss
               if (x[j] == max_age) {
                  max_age_cum_loss[i] = cum_loss[j];
               }
            }
         }
      }

      // return the maximum age cumulative loss
      return max_age_cum_loss;
   }

   /**
      * @title Calculation of maximum age by group.
      * @description Use the group and age to calculate the maximum age for each group. Will require
      * the number of rows, the number of cohorts, the cohort index, and the ages. For each group, the
      * maximum age observed for that group will be returned.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param gp A vector of groups. Each group is a different cohort.
      * @param x A vector of ages.
      * @return A vector of maximum age.
      * @examples
      * > max_age_by_gp(6, 3, c(1, 1, 1, 2, 2, 3), c(1, 2, 3, 1, 2, 1))
      * > # note that the output is a vector of length 3, not 6, because there are only 3 groups
      * > # note also that the output is sorted by group, not by age
      * > # maximum age for group 1 is 3
      * > # maximum age for group 2 is 2
      * > # maximum age for group 3 is 1
      * [1] 3 2 1
      */
   vector max_age_by_gp(int n, int n_gp, int[] gp, vector x) {
      // initialize the vector of maximum age
      vector[n_gp] max_age;
      int max_age_temp = 0;

      // loop through the groups
      for (i in 1:n_gp) {
         // initialize the maximum age for the current group
         max_age_temp = 0;         

         // loop through the ages
         for (j in 1:n) {

            // if the current group is equal to the current group in the loop, then check the age
            if (gp[j] == i) {

               // if the current age is greater than the current maximum age, then update the maximum age
               if (x[j] > max_age_temp) {
                  max_age_temp = x[j];
               }
            }
         }

         // update the maximum age for the current group
         max_age[i] = max_age_temp;
      }

      // return the maximum age
      return max_age;
   }
      
   
   /**
      * @title Calculation of chain ladder ultimate
      * @description Use the payment pattern as well as cumulative losses by cohort to calculate
      * the chain ladder ultimate loss by cohort. Will require the number of cohorts, the cumulative
      * losses, the cohort index, the ages, and the payment pattern.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param cum_loss A vector of cumulative losses by treaty.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A vector of chain ladder ultimate losses by cohort.
      */
   vector chain_ladder_ult(int n, int n_gp, vector cum_loss, int[] gp, vector x, vector G) {
      // initialize the chain ladder ultimate
      vector[n_gp] chain_ladder;

      // initialize the percent of ultimate loss by cohort
      vector[n_gp] G_gp;

      // initialize the cumulative loss by cohort
      vector[n_gp] cum_loss_gp;

      // find the cum_loss_by_gp using the cum_loss_by_gp function
      cum_loss_gp = cum_loss_by_gp(n, n_gp, cum_loss, gp, x);

      // note that the cum_loss_by_gp function does not really use the fact that it 
      // is looking at loss, so I can use it to find the the value of G by cohort
      G_gp = cum_loss_by_gp(n, n_gp, G, gp, x);

      // calculate the chain ladder ultimate
      chain_ladder = cum_loss_by_gp ./ G_by_gp;
      
      // return the chain ladder ultimate
      return chain_ladder;
   }

   /**
      * @title Calculation of Cape Cod ultimate
      * @description Use the cumulative losses, cumulative exposures, percent of ultimate loss,
      * cohort group, and ages to calculate the Cape Cod ultimate loss by cohort. Will require
      * first calculating the cumulative loss by cohort, then calculating the cumulative exposure
      * by cohort, then calculating the percent of ultimate loss by cohort, then calculating the
      * expected loss ratio, and finally calculating the Cape Cod ultimate loss by cohort.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param cum_loss A vector of cumulative losses by treaty and age.
      * @param cum_exposure A vector of cumulative exposures by treaty and age.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A vector of Cape Cod ultimate losses by cohort.
      */
   vector cape_cod_ult(int n, int n_gp, vector cum_loss, vector cum_exposure, int[] gp, vector x, vector G) {
      // initialize the Cape Cod ultimate
      vector[n_gp] cape_cod;

      // initialize the cumulative loss, cumulative exposure, and percent of ultimate loss by cohort
      vector[n_gp] cum_loss_gp;
      vector[n_gp] cum_exposure_gp;
      vector[n_gp] G_gp;

      // initialize the ELR
      real elr;

      // calculate cumulative loss by cohort
      cum_loss_gp = cum_loss_by_gp(n, n_gp, cum_loss, gp, x);

      // calculate cumulative exposure by cohort
      cum_exposure_gp = cum_loss_by_gp(n, n_gp, cum_exposure, gp, x);

      // calculate the percent of ultimate loss by cohort
      G_gp = cum_loss_by_gp(n, n_gp, G, gp, x);

      // calculate the ELR using the ELR function
      elr = ELR(n, cum_loss, cum_exposure, x, gp, G);

      // calculate the Cape Cod ultimate = (cumulative loss) + (ELR * cumulative exposure * (1 - G))
      for(i in 1:n_gp) {
         cape_cod[i] = 
            // cumulative loss
            cum_loss_gp[i] +
            
            // Cape Cod expected unrealized loss
            (  
               elr *
               cum_exposure_gp[i] *
               (1 - G_gp[i])
            );
      }

      // return the Cape Cod ultimate
      return cape_cod;
   }

   /** 
      * @title Calculation of Benktander ultimate
      * @description Use the chain ladder ultimate, Cape Cod ultimate, and percent of ultimate
      * loss to calculate the Benktander ultimate loss by cohort. Will require first calculating
      * the percent of ultimate loss by cohort, the chain ladder ultimate by cohort, and the
      * Cape Cod ultimate by cohort. Then the Benktander ultimate is calculated as the weighted
      * average of the chain ladder ultimate and the Cape Cod ultimate, where the weights given 
      * to the chain ladder is the percent of ultimate loss by cohort, and the weights given to
      * the Cape Cod ultimate is 1 - the percent of ultimate loss by cohort.
      * Calculates from first principles, so need all the variables to calculate the chain ladder
      * ultimate and the Cape Cod ultimate.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param cum_loss A vector of cumulative losses by treaty and age.
      * @param cum_exposure A vector of cumulative exposures by treaty and age.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A real number of the Benktander ultimate for each treaty.
      */
   vector benktander_ultimate(int n, int n_gp, vector cum_loss, vector cum_exposure, int[] gp, vector x, vector G) {
      // initialize the Benktander ultimate
      vector[n_gp] benktander;

      // initialize the chain ladder ultimate and the Cape Cod ultimate
      vector[n_gp] chain_ladder_ult;
      vector[n_gp] cape_cod_ult;

      // calculate the chain ladder ultimate
      chain_ladder_ult = chain_ladder_ultimate(n, n_gp, cum_loss, gp, x, G);

      // calculate the Cape Cod ultimate
      cape_cod_ult = cape_cod_ult(n, n_gp, cum_loss, cum_exposure, gp, x, G);

      // calculate the Benktander ultimate = [(chain ladder ultimate) * G] + [(Cape Cod ultimate) * (1 - G)]
      for(i in 1:n_gp) {
         benktander[i] = (chain_ladder_ult[i] * G[i]) + (cape_cod_ult[i] * (1 - G[i]));
      }
      
      // return the Benktander ultimate
      return benktander;
   } 

   /** 
      * @title Calculation mean of a triangle cell in the Clark model
      * @description Calculate the mean of a triangle cell in the Clark model. This is a 
      * general function that is meant to be called by other functions. The mean is the
      * ultimate loss for the group corresponding to the row, multiplied by the difference
      * between the current and prior percent of ultimate. Both the ultimate loss and the 
      * percent of ultimate difference are given by the `ultimate` and `G_diff` vectors,
      * respectively.
      * @param n The number of rows in the data.
      * @param ultimate A vector of ultimate losses by cohort.
      * @param G_diff A vector of the difference between the current and prior
      * percent of ultimate.
      * @return A vector of the mean of a triangle cell in the Clark model.
      */
   vector general_clark_mean(int n, vector ultimate, vector G_diff) {
      // initialize the mean
      vector[n] general_clark_mean;

      // calculate the mean = (ultimate loss) * (difference between current and prior percent of ultimate)
      for(i in 1:n) {
         general_clark_mean[i] = ultimate[i] * G_diff[i];
      }

      // return the mean
      return general_clark_mean;
   }

   

   /** 
      * @title Chain Ladder Mean of triangle cell in Clark model
      * @description Calculate the mean of a triangle cell in the Clark model. The mean is the
      * Chain Ladder ultimate multiplied by the difference between the current age and the prior age.
      * The current age is the age of the treaty at the current development period. The prior age is
      * the age of the treaty at the closest prior development period, unless the current age is the 
      * first age, in which case the prior age is 0, and so G(prior age) = 0. Will need the parameters
      * `n`, `n_gp`, `cum_loss`, `gp`, `x`, and `G` to calculate the Chain Ladder ultimate. Will 
      * also use the `inc_loss(int n, vector dev_age, vector gp, vector cum)` function to calculate
      * the incremental losses.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts. 
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param cum_loss A vector of cumulative losses by treaty and age. Will need to be converted
      * to incremental losses for the mean, using the `inc_loss(int n, vector dev_age, vector gp, vector cum)`
      * function.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A vector of length `n` with the mean of each triangle cell in the Clark model.
      * This mean is the Chain Ladder ultimate for the group corresponding to a row in the data
      * multiplied by the difference between the current age and the prior age.
      */
   vector chain_ladder_mean(int n, int n_gp, int[] gp, vector x, vector cum_loss, vector G) {
      // initialize the mean
      vector[n] cl_mean;

      // initialize the incremental mean
      vector[n] inc_mean;

      // initialize the incremental losses
      vector[n] inc_loss;

      // initialize the Chain Ladder ultimate
      vector[n_gp] cl_ult;

      // initialize the prior percent of ultimate loss
      vector[n] prior_G;

      // initialize a vector of ultimates for each row in the data, based on 
      // the corresponding group in the data
      vector[n] ult;

      // calculate the Chain Ladder ultimate
      cl_ult = chain_ladder_ultimate(n, n_gp, inc_loss, gp, x, G);

      // calculate the `ult` vector
      for(i in 1:n) {
         ult[i] = cl_ult[gp[i]];
      }

      // calculate the prior percent of ultimate loss using `prior_value(int n, vector dev_age, vector gp, vector x)`
      prior_G = prior_value(n, x, gp, G);

      // calculate the chain ladder mean incremental losses
      // using the `general_clark_mean(int n, vector ultimate, vector G_diff)` function
      inc_mean = general_clark_mean(n, ult, G - prior_G);

      // calculate the chain ladder mean cumulative losses using `cum_loss(int n, vector dev_age, vector gp, vector inc)`
      cl_mean = cum_loss(n, x, gp, inc_mean);

      // return the mean
      return cl_mean;
   }

   /**
      * @title Cape Cod Mean of triangle cell in Clark model
      * @description Calculate the mean of a triangle cell in the Clark model. The calculation 
      * is the same as the Chain Ladder mean, except that the Cape Cod ultimate is used instead
      * of the Chain Ladder ultimate. See the documentation for the `chain_ladder_mean` function
      * for more details.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param cum_loss A vector of cumulative losses by treaty and age. Will need to be converted
      * to incremental losses for the mean, using the `inc_loss(int n, vector dev_age, vector gp, vector cum)`
      * function.
      * @param cum_exposure A vector of cumulative exposure by treaty and age. Needed to calculate
      * the ELR.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A vector of length `n` with the mean of each triangle cell in the Clark model.
      * This mean is the Cape Cod ultimate for the group corresponding to a row in the data
      * multiplied by the difference between the current age and the prior age.
      */
   vector cape_cod_mean(int n, int n_gp, int[] gp, vector x, vector cum_loss, vector cum_exposure, vector G) {
      // initialize the mean
      vector[n] cc_mean;

      // initialize the incremental mean
      vector[n] inc_mean;

      // initialize the incremental losses
      vector[n] inc_loss;

      // initialize the Cape Cod ultimate
      vector[n_gp] cc_ult;

      // initialize the prior percent of ultimate loss
      vector[n] prior_G;

      // initialize a vector of ultimates for each row in the data, based on 
      // the corresponding group in the data
      vector[n] ult;

      // calculate the Cape Cod ultimate
      cc_ult = cape_cod_ultimate(n, n_gp, cum_loss, cum_exposure, gp, x, G);

      // calculate the `ult` vector
      for(i in 1:n) {
         ult[i] = cc_ult[gp[i]];
      }

      // calculate the prior percent of ultimate loss using `prior_value(int n, vector dev_age, vector gp, vector x)`
      prior_G = prior_value(n, x, gp, G);

      // calculate the Cape Cod mean incremental losses
      // using the `general_clark_mean(int n, vector ultimate, vector G_diff)` function
      inc_mean = general_clark_mean(n, ult, G - prior_G);

      // calculate the Cape Cod mean cumulative losses using `cum_loss(int n, vector dev_age, vector gp, vector inc)`
      cc_mean = cum_loss(n, x, gp, inc_mean);

      // return the mean
      return cc_mean;
   }

   /**
      * @title Benktander Mean of triangle cell in Clark model
      * @description Calculate the mean of a triangle cell in the Clark model. The calculation
      * is the same as the Chain Ladder mean, except that the Benktander ultimate is used instead
      * of the Chain Ladder ultimate. See the documentation for the `chain_ladder_mean` function
      * for more details on this, and the documentation for the `benktander_ultimate` function for
      * more details on the Benktander ultimate.
      * @param n The number of rows in the original data.
      * @param n_gp The number of cohorts.
      * @param gp A vector of groups. Each group is a different cohort. The groups should be
      * integers, starting at 1. These usually correspond to the accident year or the treaty
      * year.
      * @param x A vector of ages.
      * @param cum_loss A vector of cumulative losses by treaty and age. Will need to be converted
      * to incremental losses for the mean, using the `inc_loss(int n, vector dev_age, vector gp, vector cum)`
      * function.
      * @param cum_exposure A vector of cumulative exposure by treaty and age. Needed to calculate
      * the ELR.
      * @param G A vector with the percent of ultimate loss corresponding to each age in x.
      * @return A vector of length `n` with the mean of each triangle cell in the Clark model.
      * This mean is the Benktander ultimate for the group corresponding to a row in the data
      * multiplied by the difference between the current age and the prior age.
      */
   vector benktander_mean(int n, int n_gp, int[] gp, vector x, vector cum_loss, vector cum_exposure, vector G) {
      // initialize the mean
      vector[n] b_mean;

      // initialize the incremental mean
      vector[n] inc_mean;

      // initialize the incremental losses
      vector[n] inc_loss;

      // initialize the Benktander ultimate
      vector[n_gp] b_ult;

      // initialize the prior percent of ultimate loss
      vector[n] prior_G;

      // initialize a vector of ultimates for each row in the data, based on 
      // the corresponding group in the data
      vector[n] ult;

      // calculate the Benktander ultimate
      b_ult = benktander_ultimate(n, n_gp, cum_loss, cum_exposure, gp, x, G);

      // calculate the `ult` vector
      for(i in 1:n) {
         ult[i] = b_ult[gp[i]];
      }

      // calculate the prior percent of ultimate loss using `prior_value(int n, vector dev_age, vector gp, vector x)`
      prior_G = prior_value(n, x, gp, G);

      // calculate the Benktander mean incremental losses
      // using the `general_clark_mean(int n, vector ultimate, vector G_diff)` function
      inc_mean = general_clark_mean(n, ult, G - prior_G);

      // calculate the Benktander mean cumulative losses using `cum_loss(int n, vector dev_age, vector gp, vector inc)`
      b_mean = cum_loss(n, x, gp, inc_mean);

      // return the mean
      return b_mean;
   }
