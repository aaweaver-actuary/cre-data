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
      * @title Calculation of ELR
      * @description Use the payment pattern from the function above, as well as loss data and exposure data, to calculate the ELR using the Cape Cod formula:
      * \deqn{ELR = \frac{\sum \text{cum. loss}}{\sum \text{(cum. exposure) * G_loglogistic}}}
      * where the \code{G_loglogistic} function is the log-logistic distribution from above, and the age `x`
      * is the most recent age in the development period for the specific treaty.
      * @param n Integer number of rows in the data.
      * @param cum_loss A vector of cumulative losses.
      * @param cum_exposure A vector of cumulative exposures.
      * @param x A vector of values at which to evaluate the log-logistic cumulative distribution function.
      * @param warp A real number that controls the shape of the distribution.
      * @param theta A real number that controls the scale of the distribution.
      * @return A real number of the ELR for each treaty.
      * @examples
      * > G_loglogistic(1:5, 1, 1)
      * [1] 0.09090909 0.11111111 0.13333333 0.15789474 0.18518519
      * > elr_loglogistic(c(10, 20, 30, 40, 50), c(100, 200, 300, 400, 500), 1:5, 1, 1)
      * [1] 0.37142857
      */
   real elr_loglogistic(int n, vector cum_loss, vector cum_exposure, vector x, real warp, real theta) {
      real loss_sum = 0;
      real exposure_sum = 0;

      // calculate the sum of the product of the cumulative exposure and the log-logistic distribution
      for (i in 1:n) {
         loss_sum += cum_loss[i];
         exposure_sum += cum_exposure[i] * G_loglogistic(n, x, warp, theta)[i];
      }

      // return the ELR
      return loss_sum / exposure_sum;
   }

   /**
      * @title Calculation of chain ladder ultimate
      * @description Use the payment pattern from the function above, as well as loss data
      * to calculate the chain ladder ultimate ult = cumulative loss / G.
      * @param cum_loss A vector of cumulative losses by treaty.
      * @param G A vector of percentages of ultimate loss the cumulative loss represents.
      * @return A real number of the chain ladder ultimate for each treaty.
      * @examples
      * > chain_ladder_ult(c(10, 20, 30, 40, 50), c(0.091,0.111,0.133,0.158,0.185))
      * > // the first value is calculated as follows:
      * > // 10 / 0.091 = 109.8901
      * [1] 109.8901 180.1802 225.2252 253.1646 270.2703
      */
   vector chain_ladder_ult(vector cum_loss, vector G) {
      return cum_loss ./ G;
   }

   /**
      * @title Calculation of Cape Cod ultimate
      * @description Use the payment pattern from the function above, as well as loss data and exposure data
      * to calculate the Cape Cod ultimate ult = cumulative loss + (elr * exposure * (1 - G)).
      * @param cum_loss A vector of cumulative losses by treaty.
      * @param cum_exposure A vector of cumulative exposures by treaty.
      * @param elr A real number of the overall ELR.
      * @param G A vector of percentages of ultimate loss the cumulative loss represents.
      * @return A real number of the chain ladder ultimate for each treaty.
      * @examples
      * > cape_cod_ult(c(10, 20, 30, 40, 50), c(100, 200, 300, 400, 500), 0.37142857, c(0.091,0.111,0.133,0.158,0.185))
      * > // the first value is calculated as follows:
      * > // 10 + (0.37142857 * 100 * (1 - 0.091)) = 10 + (0.37142857 * 100 * 0.909) = 10 + (37.142857 * 0.909) = 10 + 33.571428 = 43.571428
      * [1]  43.57143  80.18018 108.10811 129.74684 144.14414
      */
   vector cape_cod_ult(vector cum_loss, vector cum_exposure, real elr, vector G) {
      return cum_loss + (elr * cum_exposure .* (1 - G));
   }

   /** 
      * @title Calculation of Benktander ultimate
      * @description Use the chain ladder ultimate, Cape Cod ultimate, and G
      * to calculate the Benktander ultimate ult = (chain ladder ultimate * G) + (Cape Cod ultimate * (1 - G)).
      * @param chain_ladder_ult A vector of chain ladder ultimate values by treaty.
      * @param cape_cod_ult A vector of Cape Cod ultimate values by treaty.
      * @param G A vector of percentages of ultimate loss as of the most recent development period for each treaty.
      * @return A real number of the Benktander ultimate for each treaty.
      * @examples
      * > benktander_ult(c(109.8901, 180.1802, 225.2252, 253.1646, 270.2703)
            , c( 43.57143,  80.18018, 108.10811, 129.74684, 144.14414)
            , c(0.091,0.111,0.133,0.158,0.185)
            )
      * > // the first value is calculated as follows:
      * > // (109.8901 * 0.091) + (43.57143 * 0.909) = 10.08901 + 39.482997 = 49.571007
      * > // the last value is calculated as follows:
      * > // (270.2703 * 0.185) + (144.14414 * 0.815) = 50.251055 + 117.893126 = 168.144181
      * [1]  49.57101  89.36036 120.12012 143.24324 168.14418
      */
   vector benktander_ult(vector chain_ladder_ult, vector cape_cod_ult, vector G) {
      // the . notation below means element-wise multiplication
      // in stan, the * operator is matrix multiplication,
      // so if I did not include the ., the result would be a matrix
      return (chain_ladder_ult .* G) + (cape_cod_ult .* (1 - G));
   }

   // convenience function to calculate the Benktander ultimate from the data instead of
   // having to pass in the chain ladder ultimate, Cape Cod ultimate, elr, and G separately
   // uses the functions above, including elr_loglogistic and G_loglogistic for the elr and G
   // calculations
   vector benktander_ultimate_from_data(int n, vector cum_loss, vector cum_exposure, vector age, vector params) {
      vector[n] G = G_loglogistic(n, age, params[1], params[2]);
      
      // calculate the chain ladder ultimate
      vector[n] chain_ladder = cum_loss ./ G;
      
      // calculate the ELR
      real elr = elr_loglogistic(n, cum_loss, cum_exposure, age, params[1], params[2]);

      // initialize the cape cod ultimate vector and the benktander ultimate vector
      vector[n] cape_cod;
      vector[n] benktander;

      for(i in 1:n){
         // calculate the cape cod ultimate
         cape_cod[n] = cum_loss[n] + (elr * cum_exposure[n] * (1 - G[n]));
      }
     
     for(i in 1:n){
         // calculate the benktander ultimate
         benktander[n] = (G[n] * chain_ladder[n] ) + ((1 - G[n]) * cape_cod[n]);
     }
     
     // return the benktander ultimate
     return benktander;
   }

   /**
      * @title Prior mean
      * @description Calculate the prior mean for each treaty. The prior mean is 0 with probability
      * `zero_prob`. The prior mean is nonzero with probability `1 - zero_prob`. If the prior mean is
      * nonzero, it is equal to the Benktander ultimate multiplied by the difference between the
      * current age and the prior age. The current age is the age of the treaty at the current
      * development period. The prior age is the age of the treaty at the prior development period.
      * @param n The number of data points.
      * @param benktander_ult A vector of length `n` with Benktander ultimate losses by treaty.
      * @param G_current A vector of length `n` with G factors by treaty, calculated at the current age.
      * @param G_prior A vector of length `n` with G factors by treaty, calculated at the prior age.
      * @param total_params A vector of length 2 with the total parameters.
      * @param zero_prob A real number between 0 and 1 representing the probability that the prior mean is 0.
      * @return A vector of length `n` of prior means by treaty.
      * @examples
      * > prior_mean(5, c(10, 10, 10, 10, 10), c(0.5, 0.5, 0.5, 0.5, 0.5), c(1, 1, 1, 1, 1), c(0, 0, 0, 0, 0), c(1, 1), 0.5)
      */
   vector prior_mean(int n, vector benktander_ult, vector G_current, vector G_prior, vector total_params) {
      // initialize a vector of length n to hold the prior mean
      vector[n] prior_mean;

      // loop through the data
      for (i in 1:n) {

         // calculate the prior mean
         prior_mean[i] = benktander_ult[i] * (G_current[i] - G_prior[i]);
      }

      // return the prior mean
      return prior_mean;
   }
      
   /**
      * @title Prior mean
      * @description Calculate the prior mean for each treaty. The prior mean is 0 with probability
      * `zero_prob`. The prior mean is nonzero with probability `1 - zero_prob`. If the prior mean is
      * nonzero, it is equal to the Benktander ultimate multiplied by the difference between the
      * current age and the prior age. The current age is the age of the treaty at the current
      * development period. The prior age is the age of the treaty at the prior development period.
      * @param n The number of data points.
      * @param treaty_id A vector of length `n` with treaty IDs.
      * @param development_period A vector of length `n` with development periods.
      * @param cumulative_loss A vector of length `n` with cumulative losses by treaty.
      * @param exposure A vector of length `n` with exposures by treaty.
      * @param total_params A vector of length 2 with the total parameters.
      * @param zero_prob A real number between 0 and 1 representing the probability that the prior mean is 0.
      * @return A vector of length `n` of prior means by treaty.
      * @examples
      * > prior_mean_from_data(5, c(1, 1, 1, 2, 2), c(1, 2, 3, 1, 2), c(10, 10, 10, 10, 10), c(1, 1), 0.5)
      */
   vector prior_mean_from_data(int n, vector treaty_id, vector development_period, vector cumulative_loss, vector exposure, vector total_params, real zero_prob) {
      // initialize a vector of length n to hold the prior mean
      vector[n] temp_prior_mean;

      // initialize vectors of length n to hold `prior_mean` inputs
      vector[n] temp_benktander_ult;
      vector[n] G_current;
      vector[n] G_prior;
      
      // calculate G_current using the G_loglogistic function defined above
      G_current = G_loglogistic(n, development_period, total_params[1], total_params[2]);

      // calculate G_prior using the G_loglogistic function defined above, but with the development period
      // that is calculated from the function `prior_dev_period` defined above
      G_prior = G_loglogistic(n, prior_dev_period(n, treaty_id, development_period), total_params[1], total_params[2]);

      // calculate benktander_ult using the benktander_ultimate function defined above
      temp_benktander_ult = benktander_ultimate_from_data(n, cumulative_loss, exposure, development_period, total_params);

      // calculate temp_prior_mean using the prior_mean function defined above
      temp_prior_mean = prior_mean(n, temp_benktander_ult, G_current, G_prior, total_params);

      // return the prior mean
      return temp_prior_mean;
   }      

   // convenience function that calculates `prior_mean_from_data` for the case where `zero_prob` is 0
   // inputs should be `n`, `treaty_id`, `development_period`, `cumulative_loss`, `exposure`, `total_params`
   // all inputs are vectors of length `n` besides `total_params`, which is a vector of length 2 
   // also includes `treaty_id` input
   /**
      * @title Prior mean
      * @description Calculate the prior mean for each treaty. The prior mean is 0 with probability
      * `zero_prob`. The prior mean is nonzero with probability `1 - zero_prob`. If the prior mean is
      * nonzero, it is equal to the Benktander ultimate multiplied by the difference between the
      * current age and the prior age. The current age is the age of the treaty at the current
      * development period. The prior age is the age of the treaty at the prior development period.
      * @param n The number of data points.
      * @param treaty_id A vector of length `n` with treaty IDs.
      * @param development_period A vector of length `n` with development periods.
      * @param cumulative_loss A vector of length `n` with cumulative losses by treaty.
      * @param exposure A vector of length `n` with exposures by treaty.
      * @param total_params A vector of length 2 with the total parameters.
      * @return A vector of length `n` of prior means by treaty.
      * @examples
      * > prior_mean_from_data_nozero(5, c(1, 1, 1, 2, 2), c(1, 2, 3, 1, 2), c(10, 10, 10, 10, 10), c(1, 1), c(1, 1))
      */
   vector prior_mean_from_data_nozero(int n, vector treaty_id, vector development_period, vector cumulative_loss, vector exposure, vector total_params) {
      // initialize a vector of length n to hold the prior mean
      vector[n] temp_prior_mean;

      // initialize vectors of length n to hold `prior_mean` inputs
      vector[n] temp_benktander_ult;
      vector[n] G_current;
      vector[n] G_prior;
      
      // calculate G_current using the G_loglogistic function defined above
      G_current = G_loglogistic(n, development_period, total_params[1], total_params[2]);

      // calculate G_prior using the G_loglogistic function defined above, but with the development period
      // that is calculated from the function `prior_dev_period` defined above
      G_prior = G_loglogistic(n, prior_dev_period(n, treaty_id, development_period), total_params[1], total_params[2]);

      // calculate benktander_ult using the benktander_ultimate function defined above
      temp_benktander_ult = benktander_ultimate_from_data(n, cumulative_loss, exposure, development_period, total_params);

      // calculate as the estimated Benktander ultimate multiplied by the difference between the 
      // percent of ultimate loss at the current development period and the percent of ultimate loss
      // at the prior development period
      temp_prior_mean = temp_benktander_ult .* (G_current - G_prior);

      // return the prior mean
      return temp_prior_mean;
   }

   // function that takes n, incremental loss per exposure and exposure and returns the cumulative paid loss
   // first multiply incr loss per exposure by exposure to get incremental loss
   // then calculate cumulative loss by passing to the inc_to_cum function defined above
   /**
        * @title Cumulative loss
        * @description Calculate the cumulative loss for each treaty. The cumulative loss is calculated
        * by multiplying the incremental loss per exposure by the exposure and then summing the incremental
        * losses by treaty.
        * @param n The number of data points.
        * @param treaty_id A vector of length `n` with treaty IDs.
        * @param incremental_loss_per_exposure A vector of length `n` with incremental losses per exposure.
        * @param exposure A vector of length `n` with exposures by treaty.
        * @return A vector of length `n` of cumulative losses by treaty.
        * @examples
        * > modeled_cumulative_loss(5, c(1, 1, 1, 2, 2), c(1, 1, 1, 1, 1), c(1, 2, 3, 4, 5))
        * [1] 1 3 6 4 9
        */
    vector modeled_cumulative_loss(int n, vector treaty_id, vector incremental_loss_per_exposure, vector exposure) {
        // initialize a vector of length n to hold the cumulative loss
        vector[n] cumulative_loss;
    
        // initialize a vector of length n to hold the incremental loss
        vector[n] incremental_loss;
    
        // calculate incremental loss by multiplying incremental loss per exposure by exposure
        incremental_loss = incremental_loss_per_exposure * exposure;
    
        // calculate cumulative loss by passing incremental loss to the inc_to_cum function defined above
        cumulative_loss = inc_to_cum(n, treaty_id, incremental_loss);
    
        // return the cumulative loss
        return cumulative_loss;
    }
