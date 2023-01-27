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
}