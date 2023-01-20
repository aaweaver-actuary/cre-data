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
   vector G_loglogistic(vector x, real warp, real theta) {
      return (x .^ warp) ./ ((x .^ warp) + (theta .^ warp));
   }

   /**
      * @title Calculation of ELR
      * @description Use the payment pattern from the function above, as well as loss data and exposure data, to calculate the ELR using the Cape Cod formula:
      * \deqn{ELR = \frac{\sum \text{cum. loss}}{\sum \text{(cum. exposure) * G_loglogistic}}}
      * where the \code{G_loglogistic} function is the log-logistic distribution from above, and the age `x`
      * is the most recent age in the development period for the specific treaty.
      * @param cum_loss A vector of cumulative losses.
      * @param cum_exposure A vector of cumulative exposures.
      * @param x A vector of values at which to evaluate the log-logistic cumulative distribution function.
      * @param warp A real number that controls the shape of the distribution.
      * @param theta A real number that controls the scale of the distribution.
      * @return A real number of the ELR for each treaty.
      * @examples
      * > G_loglogistic(1:5, 1, 1)
      * [1] 0.09090909 0.11111111 0.13333333 0.15789474 0.18518519
      * > elr(c(10, 20, 30, 40, 50), c(100, 200, 300, 400, 500), 1:5, 1, 1)
      * [1] 0.37142857
      */
   real elr_loglogistic(vector cum_loss, vector cum_exposure, vector x, real warp, real theta) {
      real loss_sum = sum(cum_loss);
      real exposure_sum;

      // calculate the sum of the product of the cumulative exposure and the log-logistic distribution
      for (i in 1:size(cum_exposure)) {
         exposure_sum += cum_exposure[i] * G_loglogistic(x[i], warp, theta);
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
   vector benktander_ult_from_data(vector cum_loss, vector cum_exposure, vector params) {
      return benktander_ult(
         chain_ladder_ult(cum_loss, G_loglogistic(cum_loss, cum_exposure, params[1], params[2])),
         cape_cod_ult(cum_loss, cum_exposure, elr_loglogistic(cum_loss, cum_exposure, params[1], params[2]), G_loglogistic(cum_loss, cum_exposure, params[1], params[2])),
         G_loglogistic(cum_loss, cum_exposure, params[1], params[2])
      );
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
}
data {
   // number of data points
   int<lower=1> N;
   
   // number of treaties in data
   int<lower=1> N_treaties;

   // number of distinct treaty periods
   int<lower=1> N_treaty_periods;

   // number of distinct development periods
   int<lower=1> N_development_periods;

   // treaty period
   vector<lower=1, upper=N_treaty_period>[N] treaty_period;

   // development period
   vector<lower=1, upper=N_development_periods>[N] development_period;

   // estimated exposure for each treaty
   vector[<lower=0>N] exposure;

   // treaty id for each data point
   vector<lower=1, upper=N_treaties>[N] treaty_id;

   // paid loss for each treaty period - development period pair
   vector[N] cumulative_paid_loss;

   // reported loss for each treaty period - dev period
   // vector[N] cumulative_reported_loss;
}
transformed data {
   // incremental data
   vector[N] incremental_paid_loss = cum_to_inc(N, cumulative_paid_loss, treaty_id);
   // vector[N] incremental_reported_loss = cum_to_inc(N, cumulative_reported_loss, treaty_id);
}
parameters {
   // total warp, total theta are highly correlated, so should be constrained
   // to be drawn from a joint distribution that has support on the positive
   // real numbers
   vector[2] total_log_params; // log of total warp and total theta

   // sigmas for the log of the total warp and total theta
   // this is the standard deviation of the log of total warp and total theta
   vector<lower=0>[2] log_param_sigmas;

   // warp and theta are the parameters 
   // and will be correlated with each other
   // correlation between warp and theta
   real<lower=-1, upper=1> rho;

   // total sigma is the standard deviation of the incremental loss per exposure
   // this is the standard deviation of the incremental loss per exposure
   real<lower=0> total_sigma;


   // there is a positive probability of an incremental loss amount being zero
   // this parameter controls the probability of zero for each data point
   // these are the hyperparameters for the zero probability
   vector[3] zero_hyperparams;
   
}
transformed parameters {
   
   // to get total warp and total theta from the log of total warp and total theta
   // we exponentiate the log of total warp and total theta
   vector[2] total_params = exp(total_log_params);

   // variance-covariance matrix for the log of total warp and total theta
   matrix[2,2] log_param_var_cov_matrix;
   // diagonal elements of the variance-covariance matrix:
   log_param_var_cov_matrix[1, 1] = log_param_sigmas[1] * log_param_sigmas[1]; // variance of log of total warp
   log_param_var_cov_matrix[2, 2] = log_param_sigmas[2] * log_param_sigmas[2]; // variance of log of total theta

   // off-diagonal elements of the variance-covariance matrix:
   log_param_var_cov_matrix[1, 2] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta
   log_param_var_cov_matrix[2, 1] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta
   
   // the probability of an incremental loss amount being zero is a function of
   // the cumulative loss from the prior period, the development period, and the exposure
   vector<lower=0, upper=1>[N] zero_prob = inv_logit(
      zero_hyperparams[1] * prior_cum_loss(N, treaty_id, development_period, cumulative_paid_loss) +
      zero_hyperparams[2] * development_period + 
      zero_hyperparams[3] * exposure);
   
   
}
model{
   // correlation parameter is selected from a distribution with support on the
   // interval [-1, 1] 
   rho ~ uniform(-1, 1);

   // the standard deviations of the log of total warp and total theta are selected
   // from a distribution with support on the positive real numbers
   // this time I am using a half Cauchy distribution, which has support on the
   // positive real numbers and also has a heavier tail than the uniform distribution
   // this means that the standard deviations of the log of total warp and total theta
   // are more likely to be large than small
   // a half Cauchy distribution is implemented in Stan using the cauchy distribution
   sigma_log_theta ~ cauchy(0, 1);
   sigma_log_warp ~ cauchy(0, 1);
   

   // the log of total warp and total theta are selected from a multivariate normal
   // distribution with mean zero and covariance matrix log_param_var_cov_matrix
   total_log_params ~ multi_normal(rep_vector(0, 2), log_param_var_cov_matrix);

   // select zero_hyperparams from a normal distribution with mean
   // zero and standard deviation 1
   zero_hyperparams ~ normal(0, 1);

   // the incremental paid loss per exposure is selected from a distribution with mean
   // (prior_mean / exposure) and standard deviation total_sigma
   // it is assumed that the incremental paid loss per exposure can take values
   // on the real numbers, but is skewed towards the right, and also has a positive
   // probability of being zero. instead of using a mixture distribution, I am using
   // conditional probability to model the probability of zero and the probability
   // of a non-zero value separately
   // the probability of zero is modeled using the zero_prob vector
   // the probability of a non-zero value is modeled using the normal distribution
   // with mean (prior_mean / exposure) and standard deviation total_sigma
   incremental_paid_loss ~ normal(
      // 
      prior_mean_from_data(N, treaty_id, development_period, cumulative_paid_loss) / exposure,


   
   


   

   
     
}