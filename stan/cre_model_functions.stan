functions {
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
      * @title Log-logistic distribution
      * @description The log-logistic distribution is a continuous probability distribution with parameters \code{warp} and \code{theta}. It is a member of the family of generalized logistic distributions.
      * @param n Integer number of rows in the data.
      * @param x A vector of values at which to evaluate the log-logistic distribution.
      * @param warp A real number that controls the shape of the distribution.
      * @param theta A real number that controls the scale of the distribution.
      * @return A vector of values of the log-logistic distribution at the values specified by \code{x}.
      * @references \url{https://en.wikipedia.org/wiki/Log-logistic_distribution}
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
   vector benktander_ult_from_data(int n, vector cum_loss, vector cum_exposure, vector age, vector params) {
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
      * @title Cumulative to incremental
      * @description Convert cumulative loss to incremental loss. This is done by subtracting
      * the cumulative loss from the previous cumulative loss, where previous means one
      * development period earlier. If the treaty is in the first development period, the
      * incremental loss is the same as the cumulative loss.
      * @param N The number of data points.
      * @param cum_loss A vector of length `N` with cumulative losses by treaty.
      * @param treaty_id A vector of length `N` with treaty IDs for each treaty.
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

      // initialize a variable to hold the previous treaty ID
      // to check if the current treaty ID is the same as the previous one
      int prev_treaty_id = 0;

      // initialize a variable to hold the previous cumulative loss
      real prev_cum_loss = 0;

      // loop through the data
      for (n in 1:N) {

         // if the current treaty ID is the same as the previous one,
         if (treaty_id[n] == prev_treaty_id) {

            // subtract the previous cumulative loss from the current cumulative loss
            inc_loss[n] = cum_loss[n] - prev_cum_loss;
         }
         
         // if the current treaty ID is not the same as the previous one,
         else {

            // the incremental loss is the same as the cumulative loss
            inc_loss[n] = cum_loss[n];
         }

         // update the previous treaty ID and previous cumulative loss
         // so that they can be used in the next iteration of the loop
         prev_treaty_id = treaty_id[n];
         prev_cum_loss = cum_loss[n];
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
    
        // initialize a variable to hold the previous treaty ID
        // to check if the current treaty ID is the same as the previous one
        int prev_treaty_id = 0;
    
        // initialize a variable to hold the previous cumulative loss
        real prev_cum_loss = 0;
    
        // loop through the data
        for (n in 1:N) {
    
             // if the current treaty ID is the same as the previous one,
             if (treaty_id[n] == prev_treaty_id) {
    
                // add the previous cumulative loss to the current incremental loss
                cum_loss[n] = inc_loss[n] + prev_cum_loss;
             }
             
             // if the current treaty ID is not the same as the previous one,
             else {
    
                // the cumulative loss is the same as the incremental loss
                cum_loss[n] = inc_loss[n];
             }
    
             // update the previous treaty ID and previous cumulative loss
             // so that they can be used in the next iteration of the loop
             prev_treaty_id = treaty_id[n];
             prev_cum_loss = cum_loss[n];
        }
    
        // return the cumulative loss
        return cum_loss;

   // function that calculates the prior mean as defined below:
   // prior mean is 0 with proability zero_prob
   // prior mean is nonzero with probability 1 - zero_prob
   // if prior mean is nonzero, it is equal to
   // Benktander ultimate * (G(current age, total_params[1], total_params[2]) - G(prior age, total_params[1], total_params[2]))
   // inputs should be `n`, `benktander_ult`, `G`, `current_age`, `prior_age`, and `total_params`
   // all inputs are vectors of length `n` besides `total_params`, which is a vector of length 2
   // also includes real `zero_prob` input
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
   vector prior_mean(int n, vector benktander_ult, vector G_current, vector G_prior, vector total_params, real zero_prob) {
      // initialize a vector of length n to hold the prior mean
      vector[n] prior_mean;

      // loop through the data
      for (i in 1:n) {

         // if the prior mean is 0,
         if (bernoulli_rng(zero_prob)) {

            // set the prior mean to 0
            prior_mean[i] = 0;
         }

         // if the prior mean is nonzero,
         else {

            // calculate the prior mean
            prior_mean[i] = benktander_ult[i] * (G_current[i] - G_prior[i]);
         }
      }

      // return the prior mean
      return prior_mean;
   }

   // convenience function that calculates the prior mean as defined below, but calculates the G factors and Benktander ultimate
   // similarly to the convenience function for the benktander ultimate defined above
   // inputs should be `n`, `development_period`, `cumulative_loss`, `total_params`, and `zero_prob`
   // all inputs are vectors of length `n` besides `total_params`, which is a vector of length 2 and `zero_prob`, which is a real number
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
      * @param zero_prob A real number between 0 and 1 representing the probability that the prior mean is 0.
      * @return A vector of length `n` of prior means by treaty.
      * @examples
      * > prior_mean_from_data(5, c(1, 1, 1, 2, 2), c(1, 2, 3, 1, 2), c(10, 10, 10, 10, 10), c(1, 1), 0.5)
      */
   vector prior_mean_from_data(int n, vector treaty_id, vector development_period, vector cumulative_loss, vector exposure, vector total_params, real zero_prob) {
      // initialize a vector of length n to hold the prior mean
      vector[n] prior_mean;

      // initialize vectors of length n to hold `prior_mean` inputs
      vector[n] benktander_ult;
      vector[n] G_current;
      vector[n] G_prior;
      
      // calculate G_current using the G_loglogistic function defined above
      G_current = G_loglogistic(n, treaty_id, development_period, cumulative_loss, total_params);

      // calculate G_prior using the G_loglogistic function defined above, but with the development period
      // that is calculated from the function `prior_development_period` defined above
      G_prior = G_loglogistic(n, treaty_id, prior_development_period(n, treaty_id, development_period), cumulative_loss, total_params);

      // calculate benktander_ult using the benktander_ultimate function defined above
      benktander_ult = benktander_ultimate_from_data(n, cumulative_loss, exposure, total_params);

      // calculate prior_mean using the prior_mean function defined above
      prior_mean = prior_mean(n, benktander_ult, G_current, G_prior, total_params, zero_prob);

      // return the prior mean
      return prior_mean;
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
      vector[n] prior_mean;

      // initialize vectors of length n to hold `prior_mean` inputs
      vector[n] benktander_ult;
      vector[n] G_current;
      vector[n] G_prior;
      
      // calculate G_current using the G_loglogistic function defined above
      G_current = G_loglogistic(n, treaty_id, development_period, cumulative_loss, total_params);

      // calculate G_prior using the G_loglogistic function defined above, but with the development period
      // that is calculated from the function `prior_development_period` defined above
      G_prior = G_loglogistic(n, treaty_id, prior_development_period(n, treaty_id, development_period), cumulative_loss, total_params);

      // calculate benktander_ult using the benktander_ultimate function defined above
      benktander_ult = benktander_ultimate_from_data(n, cumulative_loss, exposure, total_params);

      // calculate as the estimated Benktander ultimate multiplied by the difference between the 
      // percent of ultimate loss at the current development period and the percent of ultimate loss
      // at the prior development period
      prior_mean = benktander_ult * (G_current - G_prior);

      // return the prior mean
      return prior_mean;
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
