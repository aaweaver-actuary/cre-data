/**
    * @title: Calculate initial mu parameter from a vector of data.
    * @description: Calculate initial mu parameter from a vector of data.
    * @param: x - vector of data
    * @return: mu - initial mu parameter
    * @references: https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution#Parameter_estimation
    */
    real initial_mu(vector x) {
        // initialize mu
        real mu = 0;

        // initialize m = mean, s = standard deviation, gamma = skewness
        real m = mean(x);
        real s = sd(x);
        real gamma = skewness(x);

        // mu = m - [s * (gamma / 2) ^ (1/3)]
        mu = m - (s * pow(gamma / 2, 1 / 3));
        return mu;
    }

/**
    * @title: Calculate initial sigma parameter from a vector of data.
    * @description: Calculate initial sigma parameter from a vector of data.
    * @param: x - vector of data
    * @return: sigma - initial sigma parameter
    * @references: https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution#Parameter_estimation
    */
    real initial_sigma(vector x) {
        // initialize sigma and sigma2
        real sigma = 0;
        real sigma2 = 0;

        // initialize m = mean, s = standard deviation, gamma = skewness
        real m = mean(x);
        real s = sd(x);
        real gamma = skewness(x);

        // sigma2 = (s^2) * (1 - [gamma / 2] ^ (2/3))
        sigma2 = pow(s, 2) * (1 - pow(gamma / 2, 2 / 3));

        // sigma = sqrt(sigma2)
        sigma = sqrt(sigma2);
        
        return sigma;
    }

/**
    * @title: Calculate initial tau parameter from a vector of data.
    * @description: Calculate initial tau parameter from a vector of data.
    * @param: x - vector of data
    * @return: tau - initial tau parameter
    * @references: https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution#Parameter_estimation
    */
    real initial_tau(vector x) {
        // initialize tau
        real tau = 0;

        // initialize m = mean, s = standard deviation, gamma = skewness
        real m = mean(x);
        real s = sd(x);
        real gamma = skewness(x);

        // tau = s * [(gamma / 2) ^ (1/3)]
        tau = s * pow(gamma / 2, 1 / 3);

        // return tau
        return tau;
    }