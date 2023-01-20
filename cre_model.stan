functions {
   #include "cre_model_functions.stan"
   #include "loss_functions.stan"
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

   // vector of prior estimates of the warp, theta, and sigma parameters
   // (in that order) for the cumulative paid loss
   vector[3] prior_params;
}
transformed data {
   // incremental data
   vector[N] incremental_paid_loss = cum_to_inc(N, cumulative_paid_loss, treaty_id);
   // vector[N] incremental_reported_loss = cum_to_inc(N, cumulative_reported_loss, treaty_id);

   // incremental loss per exposure
   vector[N] incremental_paid_loss_per_exposure = incremental_paid_loss / exposure;

   // prior log parameters
   vector[2] prior_log_params = log(prior_params[1:2]);
}
parameters {
   // parameters are nonnegative and skewed to the right, so we use a lognormal distribution
   // only two parameters: warp and theta
   vector[2] total_log_params; // log of total warp and total theta

   // sigmas for the log of the total warp and total theta
   vector<lower=0>[2] log_param_sigmas;

   // correlation parameter for the log of total warp and total theta
   real<lower=-1, upper=1> rho;

   // total sigma is the standard deviation of the incremental loss per exposure
   real<lower=0> total_sigma;

   // skewness parameter for the incremental loss per exposure
   real loss_skew;

   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // these are the hyperparameters for the zero probability
   // vector[3] zero_hyperparams;
}
transformed parameters {
   // these are the parameters that are used in the model
   vector[2] total_params = exp(total_log_params);

   // variance-covariance matrix for the log of total warp and total theta
   matrix[2,2] log_param_var_cov_matrix;
   log_param_var_cov_matrix[1, 1] = log_param_sigmas[1] * log_param_sigmas[1]; // variance of log of total warp (diagonal element)
   log_param_var_cov_matrix[2, 2] = log_param_sigmas[2] * log_param_sigmas[2]; // variance of log of total theta (diagonal element)
   log_param_var_cov_matrix[1, 2] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   log_param_var_cov_matrix[2, 1] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)

   // loss measures

   // MSE of the cumulative paid loss (uses modelled_cumulative_loss function)
   real mse_cum_paid_loss = mean((cumulative_paid_loss -
   modeled_cumulative_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure)) ^ 2);
   
   real mae_cum_paid_loss = fabs(cumulative_paid_loss -
   modeled_cumulative_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure));

   
   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // the probability of an incremental loss amount being zero is a function of
   // the cumulative loss from the prior period, the development period, and the exposure
   // vector<lower=0, upper=1>[N] zero_prob = inv_logit(
   //    zero_hyperparams[1] * prior_cum_loss(N, treaty_id, development_period, cumulative_paid_loss) +
   //    zero_hyperparams[2] * development_period + 
   //    zero_hyperparams[3] * exposure);
}
model{
   // correlation parameter is selected from the interval [-1, 1] 
   rho ~ uniform(-1, 1);

   // sigmas for the log of total warp and total theta are selected from a cauchy distribution
   // with mean zero and standard deviation 1
   // this distribution form is used because the sigmas are nonnegative and skewed to the right
   // and the cauchy distribution is the conjugate prior for the log of a nonnegative skewed
   // to the right distribution
   sigma_log_theta ~ cauchy(0, 1);
   sigma_log_warp ~ cauchy(0, 1);

   // log parameters are drawn from a multivariate normal distribution with mean 
   // equal to the prior log parameters `prior_log_params`
   // and variance-covariance matrix `log_param_var_cov_matrix`
   total_log_params ~ multi_normal(prior_log_params, log_param_var_cov_matrix);

   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // select zero_hyperparams from a normal distribution with mean
   // zero and standard deviation 1   
   // zero_hyperparams ~ normal(0, 1);

   // the incremental paid loss per exposure is selected from a skewed distribution
   // with skewness controlled by a parameter called `loss_skew`
   loss_skew ~ uniform(0, 1);

   // the incremental paid loss per exposure is selected from an exponential modified normal distribution
   // with mean equal to the estimate of incremental loss based on the benktander ultimate
   // and standard deviation equal to `total_sigma`
   // and skewness equal to `loss_skew`   
   incremental_paid_loss_per_exposure ~ exp_mod_normal(
      prior_mean(N, treaty_id, development_period, cumulative_paid_loss, exposure, exp(total_log_params)) / exposure,
      total_sigma,                               
      loss_skew
      );
}