// not including any user-defined functions in this file
// they need to be imported from the "cre_model_functions.stan" file
// which is included in the same folder as this file

// this is the model for the cumulative paid loss
// the model is a hierarchical model with an exponentially-modified
// normal distribution for the incremental loss per exposure

// import the user-defined functions:
functions {
   #include "cre_model_functions.stan"
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

   // number of modelling groups
   int<lower=1> N_groups;

   // number of lines of business
   int<lower=1> N_lines_of_business;

   // treaty period
   vector<lower=1, upper=N_treaty_period>[N] treaty_period;

   // development period
   vector<lower=1, upper=N_development_periods>[N] development_period;

   // estimated exposure for each treaty
   vector[<lower=0>N] exposure;

   // treaty id for each data point
   vector<lower=1, upper=N_treaties>[N] treaty_id;

   // modelling group id for each data point
   vector<lower=1, upper=N_groups>[N] group_id;

   // line of business id for each data point
   vector<lower=1, upper=N_lines_of_business>[N] line_of_business_id;

   // paid loss for each treaty period - development period pair
   vector[N] cumulative_paid_loss;

   // reported loss for each treaty period - dev period
   // vector[N] cumulative_reported_loss;

   // matrix of prior estimates of the warp, theta, and elr parameters
   // (in that order) for the cumulative paid loss, one for each group
   matrix[N_groups, 3] prior_params;
}
transformed data {
   // incremental data
   vector[N] incremental_paid_loss = cum_to_inc(N, cumulative_paid_loss, treaty_id);
   // vector[N] incremental_reported_loss = cum_to_inc(N, cumulative_reported_loss, treaty_id);

   // incremental loss per exposure
   vector[N] incremental_paid_loss_per_exposure = incremental_paid_loss / exposure;

   // prior log parameters
   matrix[N_groups, 3] prior_log_params = log(prior_params);
}
parameters {
   // parameters are nonnegative and skewed to the right, so we use a lognormal distribution
   // only two parameters: warp and theta
   matrix[N_groups, 2] total_log_params;

   // sigmas for the log of the total warp and total theta
   matrix<lower=0>[N_groups, 2] log_param_sigmas;

   // correlation parameter for the log of total warp and total theta
   vector<lower=-1, upper=1>[N_groups] rho;

   // total sigma is the standard deviation of the incremental loss per exposure
   real<lower=0>[N_groups] total_sigma;

   // skewness parameter for the incremental loss per exposure
   real loss_skew[N_groups];

   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // these are the hyperparameters for the zero probability
   // vector[3] zero_hyperparams;
}
transformed parameters {
   // these are the parameters that are used in the model
   // total parameters
   matrix[N_groups, 2] total_params = exp(total_log_params);

   // variance-covariance matrix for the log of total warp and total theta, for each group
   matrix[N_groups, 3, 3] log_param_var_cov_matrix;
   // need to do the following for each group
   // log_param_var_cov_matrix[1, 1] = log_param_sigmas[1] * log_param_sigmas[1]; // variance of log of total warp (diagonal element)
   // log_param_var_cov_matrix[2, 2] = log_param_sigmas[2] * log_param_sigmas[2]; // variance of log of total theta (diagonal element)
   // log_param_var_cov_matrix[1, 2] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   // log_param_var_cov_matrix[2, 1] = rho * log_param_sigmas[1] * log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   for(g in 1:N_groups){
      log_param_var_cov_matrix[g, 1, 1] = log_param_sigmas[g, 1] * log_param_sigmas[g, 1]; // variance of log of total warp (diagonal element)
      log_param_var_cov_matrix[g, 2, 2] = log_param_sigmas[g, 2] * log_param_sigmas[g, 2]; // variance of log of total theta (diagonal element)
      log_param_var_cov_matrix[g, 1, 2] = rho[g] * log_param_sigmas[g, 1] * log_param_sigmas[g, 2]; // covariance of log of total warp and log of total theta (off-diagonal element)
      log_param_var_cov_matrix[g, 2, 1] = rho[g] * log_param_sigmas[g, 1] * log_param_sigmas[g, 2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   }
   

   // loss measures

   
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
=======
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
   real mean_square_error_cum_paid_loss = mean_square_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);
   real mean_absolute_error_cum_paid_loss = mean_absolute_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);
   real mean_asymmetric_error_cum_paid_loss = mean_asymmetric_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);

   
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
// to optimize the model in stan, using stan's built-in optimization algorithm
// we want to optimize the mean asymmetric error for the cumulative paid loss

// this is the target function

generated quantities {
   // cumulative loss amounts
   vector[N] modeled_cumulative_paid_loss = modeled_cumulative_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure)
   
   // loss measures
   real mean_square_error_cum_paid_loss = mean_square_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);
   real mean_absolute_error_cum_paid_loss = mean_absolute_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);
   real mean_asymmetric_error_cum_paid_loss = mean_asymmetric_error_cum_loss(N, treaty_id, incremental_paid_loss_per_exposure, exposure);
}

>>>>>>> 9314363b595980b6d1be602f129340262e31858d