functions{
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
}