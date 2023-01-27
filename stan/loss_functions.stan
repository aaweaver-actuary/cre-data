
    // this script contains calculated loss functions for optimization of the cumulative loss function

    /**
    * @title Mean Squared Error Loss Function
    * @description This function calculates the mean squared error loss function for a given set of data points
    *  by first calculating the modeled cumulative loss and then calculating the squared error between the modeled
    *  cumulative loss and the actual cumulative loss. The mean of the squared error is then returned.
    * @param N int number of data points
    * @param treaty_id vector of treaty ids
    * @param incremental_loss_per_exposure vector of incremental loss per exposure
    * @param exposure vector of exposure
    * @param cumulative_loss vector of cumulative loss
    * @return real mean squared error loss
    * @example
    * > mse_cummean_square_error_cum_loss_loss(3, [1, 1, 2], [0.5, 1.7, 3.2], [10, 20, 30], [1, 2, 3])
    */
    real mean_square_error_cum_loss(int N, vector treaty_id, vector incremental_loss_per_exposure, vector exposure, vector cumulative_loss) {
        vector[N] temp_modeled_cumulative_loss;
        vector[N] squared_error;
        
        temp_modeled_cumulative_loss = modeled_cumulative_loss(N, treaty_id, incremental_loss_per_exposure, exposure);

        squared_error = square(cumulative_loss - temp_modeled_cumulative_loss);

        return mean(squared_error);
    }

    /**
    * @title Mean Absolute Error Loss Function
    * @description This function calculates the mean absolute error loss function for a given set of data points
    *  by first calculating the modeled cumulative loss and then calculating the absolute error between the modeled
    *  cumulative loss and the actual cumulative loss. The mean of the absolute error is then returned.
    * @param N int number of data points
    * @param treaty_id vector of treaty ids
    * @param incremental_loss_per_exposure vector of incremental loss per exposure
    * @param exposure vector of exposure
    * @param cumulative_loss vector of cumulative loss
    * @return real mean absolute error loss
    * @example
    * > mean_absolute_error_cum_loss(3, [1, 1, 2], [1, 2, 3], [1, 2, 3], [1, 2, 3])
    */
    real mean_absolute_error_cum_loss(int N, vector treaty_id, vector incremental_loss_per_exposure, vector exposure, vector cumulative_loss) {
        vector[N] temp_modeled_cumulative_loss;
        vector[N] absolute_error;
        
        temp_modeled_cumulative_loss = modeled_cumulative_loss(N, treaty_id, incremental_loss_per_exposure, exposure);

        absolute_error = fabs(cumulative_loss - modeled_cumulative_loss);

        return mean(absolute_error);
    }

    /**
    * @title Mean Asymmetric Error Loss Function
    * @description This function calculates the mean asymmetric error loss function for a given set of data points
    *  by first calculating the modeled cumulative loss and then calculating the asymmetric error between the modeled
    *  cumulative loss and the actual cumulative loss. If actual > modeled, error is squared and if actual <= modeled,
    *  error is absolute. The mean of the asymmetric error is then returned. This loss function is useful when the
    *  model is underestimating the cumulative loss, or when you want to penalize underestimation more than overestimation 
    *  due to corporate risk appetite.
    * @param N int number of data points
    * @param treaty_id vector of treaty ids
    * @param incremental_loss_per_exposure vector of incremental loss per exposure
    * @param exposure vector of exposure
    * @param cumulative_loss vector of cumulative loss
    * @return real mean asymmetric error loss
    * @example
    * > mean_asymmetric_error_cum_loss(3, [1, 1, 2], [1, 2, 3], [1, 2, 3], [1, 2, 3])
    */
    real mean_asymmetric_error_cum_loss(int N, vector treaty_id, vector incremental_loss_per_exposure, vector exposure, vector cumulative_loss) {
        vector[N] modeled_cumulative_loss;
        vector[N] asymmetric_error;
        
        modeled_cumulative_loss = modeled_cumulative_loss(N, treaty_id, incremental_loss_per_exposure, exposure)

        for (i in 1:N) {
            if (cumulative_loss[i] > modeled_cumulative_loss[i]) {
                asymmetric_error[i] = (cumulative_loss[i] - modeled_cumulative_loss[i])^2;
            } else {
                asymmetric_error[i] = fabs(cumulative_loss[i] - modeled_cumulative_loss[i]);
            }
        }

        return mean(asymmetric_error);
    }
