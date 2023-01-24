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
   vector[2] total_log_params;
   matrix[N_groups, 2] group_log_params;

   // sigmas for the log of the total warp and total theta
   vector<lower=0>[2] total_log_param_sigmas;
   matrix<lower=0>[N_groups, 2] log_param_sigmas;

   // correlation parameter for the log of total warp and total theta
   real<lower=-1, upper=1> total_rho;
   vector<lower=-1, upper=1>[N_groups] rho;

   // total sigma is the standard deviation of the incremental loss per exposure
   real<lower=0> total_sigma;
   vector<lower=0>[N_groups] group_sigma;

   // skewness parameter for the incremental loss per exposure
   real total_loss_skew;
   vector group_loss_skew[N_groups];

   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // these are the hyperparameters for the zero probability
   // vector[3] zero_hyperparams;
}
transformed parameters {
   // these are the parameters that are used in the model
   // total parameters
   vector[2] total_params = exp(total_log_params);
   matrix[N_groups, 2] group_params = exp(group_log_params);

   // variance-covariance matrix for the log of total warp and total theta, for the total parameters
   matrix[3, 3] total_log_param_var_cov_matrix;
   total_log_param_var_cov_matrix[1, 1] = total_log_param_sigmas[1] * total_log_param_sigmas[1]; // variance of log of total warp (diagonal element)
   total_log_param_var_cov_matrix[2, 2] = total_log_param_sigmas[2] * total_log_param_sigmas[2]; // variance of log of total theta (diagonal element)
   total_log_param_var_cov_matrix[1, 2] = total_rho * total_log_param_sigmas[1] * total_log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   total_log_param_var_cov_matrix[2, 1] = total_rho * total_log_param_sigmas[1] * total_log_param_sigmas[2]; // covariance of log of total warp and log of total theta (off-diagonal element)

   // variance-covariance matrix for the log of total warp and total theta, for the group parameters
   matrix[N_groups, 3, 3] log_param_var_cov_matrix;
   for(g in 1:N_groups){
      log_param_var_cov_matrix[g, 1, 1] = log_param_sigmas[g, 1] * log_param_sigmas[g, 1]; // variance of log of total warp (diagonal element)
      log_param_var_cov_matrix[g, 2, 2] = log_param_sigmas[g, 2] * log_param_sigmas[g, 2]; // variance of log of total theta (diagonal element)
      log_param_var_cov_matrix[g, 1, 2] = rho[g] * log_param_sigmas[g, 1] * log_param_sigmas[g, 2]; // covariance of log of total warp and log of total theta (off-diagonal element)
      log_param_var_cov_matrix[g, 2, 1] = rho[g] * log_param_sigmas[g, 1] * log_param_sigmas[g, 2]; // covariance of log of total warp and log of total theta (off-diagonal element)
   }

   // skewness parameters first total, then by group, where the group parameters
   // start with the total parameters and then are adjusted by the group skewness
   // 

   real a = lognormal_rng(0, 1);
   real b = lognormal_rng(0, 1);
   vector[N_groups] a_gp = normal_rng(a, 0.1, N_groups);
   vector[N_groups] b_gp = normal_rng(b, 0.1, N_groups);
   

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
   // (this is the support of the bivariate normal distribution)
   total_rho ~ uniform(-1, 1);
   rho ~ uniform(-1, 1);

   // sigmas for the log of total warp and total theta are selected from a cauchy distribution
   // with mean zero and standard deviation 1
   // this distribution form is used because the sigmas are nonnegative and skewed to the right
   // and the cauchy distribution is the conjugate prior for the log of a nonnegative skewed
   // to the right distribution
   total_log_param_sigmas ~ cauchy(0, 1);
   log_param_sigmas ~ cauchy(0, 1);
   
   // log parameters are drawn from a multivariate normal distribution with mean 
   // equal to the prior log parameters `prior_log_params`
   // and variance-covariance matrix `log_param_var_cov_matrix`
   // total_log_params ~ multi_normal(prior_log_params, log_param_var_cov_matrix);
   total_log_params ~ multi_normal(prior_log_params, total_log_param_var_cov_matrix);
   group_log_params ~ multi_normal(prior_log_params, log_param_var_cov_matrix);


   // ==============================================================================
   // leaving this out for now -- will hopefully add back in later =================
   // ==============================================================================
   // select zero_hyperparams from a normal distribution with mean
   // zero and standard deviation 1   
   // zero_hyperparams ~ normal(0, 1);

   // the incremental paid loss per exposure is selected from a skewed distribution
   // with skewness controlled by a parameter `total_loss_skew` for the total
   // and `group_loss_skew` for the group
   // typical prior distributions for a skewness parameter are to use depends on the
   // following questions:
   // 1. is the skewness parameter positive or negative? is it possible for it to be zero?
   //    in our case, the skewness parameter is negative and can be zero
   // 2. is the skewness parameter bounded? if so, what is the upper bound? in our case, the
   //    skewness parameter is bounded by -1 and 1
   // 3. is the skewness parameter continuous or discrete? in our case, the skewness parameter
   //    is continuous
   // 4. is the skewness parameter symmetric or asymmetric? in our case, the skewness parameter
   //    is asymmetric
   // 5. is the skewness parameter unimodal or multimodal? in our case, the skewness parameter
   //    is unimodal
   // 6. is the skewness parameter known to be positive or negative? in our case, the skewness
   //    parameter is NOT known to be EITHER positive or negative
   // this discussion leads to the following prior distributions, since we require a bounded distribution:
   // 1. beta distribution: this is a continuous distribution that is bounded between 0 and 1
   //    and is symmetric, but can be scaled to be asymmetric and bounded between -1 and 1
   
   total_loss_skew ~ beta(a, b);

   // a and b are hyperparameters that force the distribution to be bounded between -1 and 1
   // a_gp and b_gp are terms that are added to a and b to allow the group skewness to vary by group
   group_loss_skew ~ beta(a_gp, b_gp);

   // the incremental paid loss per exposure is selected from an exponential modified normal distribution
   // with mean equal to the estimate of incremental loss based on the benktander ultimate
   // using the prior_mean_from_data_nozero(n, treaty_id, development_period, cumulative_loss, exposure, total_params)
   // function, which is the same as the prior mean function except that it does not include the zero probability
   // and standard deviation equal to `total_sigma`
   // and skewness equal to `loss_skew`   
   incremental_paid_loss_per_exposure ~ exp_mod_normal(
      // first parameter is the mean, which is the estimate of incremental loss based on the benktander ultimate
      // and divided by the exposure
      prior_mean_from_data_nozero(N, treaty_id, development_period, cumulative_loss, exposure, total_params) / exposure,

      // second parameter is the standard deviation, which is the total sigma, and is already divided by the exposure
      total_sigma,                               
      
      // third parameter is the skewness, which is the total loss skew, and is already divided by the exposure
      total_loss_skew
      );
}

generated quantities {
   // incremental paid loss per exposure gets multiplied by the exposure to get the incremental paid loss
   real incremental_paid_loss = incremental_paid_loss_per_exposure * exposure;

   // calculate the cumulative paid loss using the inc_to_cum function from the `cre_model_functions.stan` file
   real cumulative_paid_loss = inc_to_cum(N, treaty_id, development_period, incremental_paid_loss, cumulative_paid_loss);
}
