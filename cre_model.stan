functions {
   /* function that takes a vector x, positive real number `warp`, positive real number `theta` */
   /* and returns (x ^ warp) / ((x ^ warp) + (theta ^ warp))*/
   vector loglogistic(vector x, real warp, real theta) {
      return (x .^ warp) ./ ((x .^ warp) + (theta .^ warp));
   }
}
data {
   /* number of data points */
    int<lower=1> N;
   
   /* number of treaties in data */
   int<lower=1> N_treaties;

   /* number of distinct treaty periods */
    int<lower=1> N_treaty_periods;

    /* number of distinct development periods */
    int<lower=1> N_development_periods;

    /* treaty period */
   vector<lower=1, upper=N_treaty_period>[N] treaty_period;

    /* development period */
    vector<lower=1, upper=N_development_periods>[N_treaties] development_period;

    /* paid loss for each treaty period - development period pair*/
    vector[N_treaties] paid_loss;


}
