import numpy as np
from datetime import datetime
from govcan_data_manager import Time, get_bond_data

def predict_bond(time: Time, future_months=60, target_rate=None):
    '''
    Predict future rates of return based on time profile
    
    Using Targeted Monte-Carlo Simulation:
    - Diff rates per time profile
    - Diff seasonal patterns (market seasonality)
    - Diff volatility levels
    '''
    
    # Historical data for both bounds
    dates_low, vals_low, dates_high, vals_high = get_bond_data(time)
    
    # If target rate was not specified
    if target_rate is None:
        if time == Time.SHORT:
            target_rate = 5.0 # conservative
        elif time == Time.MED:
            target_rate = 5.5 # balanced
        else:
            target_rate = 6.5
            
    cur_rate = (vals_low[-1] + vals_high[-1]) / 2
    
    # Future dates
    last_date = max(dates_low[-1], dates_high[-1])
    days_per_month  =  30.44
    future_dates = np.array([
        last_date + (days_per_month * i * 24 * 60 * 60) # convert to seconds
        for i in range(1, future_months + 1)
    ])
    
    # Prediction parameters
    predictions = np.zeros(future_months)
    confidence_intervals = np.zeros((future_months, 2))
    
    convergence_period = 36 * int(days_per_month)
    year_cycle = 12 * int(days_per_month)
    
    # Market seasonality params
    seasonal_amp = 0.02 # 2%
    
    if time == Time.SHORT:
        volatility = 0.08
    elif time == Time.MED:
        volatility = 0.14
    else:
        volatility = 0.20
        
    for i in range(future_months):
        day_index = i * int(days_per_month)
        month = i % 12
        
        if day_index < convergence_period:
            weight = (convergence_period - day_index) / convergence_period
            base_prediction = cur_rate * weight + target_rate * (1 - weight)
        else:
            base_prediction = target_rate
            
        # Market seasonality (January Effct)
        seasonal = seasonal_amp * np.sin(2 * np.pi * day_index / year_cycle)
        if month in [11, 0]:
            seasonal *= 1.5
            
        # Random variation
        time_weight = min(1.0, day_index / (24 * days_per_month))
        random_variation = np.random.normal(0, volatility * (1 - time_weight))
        
        predictions[i] = base_prediction + seasonal + random_variation
        
        # Confidence interval calc
        years_out = i / 12
        int_width = volatility * (1 + years_out * 0.1)
        confidence_intervals[i] = [
            predictions[i] - int_width,
            predictions[i] + int_width
        ]
        
    # Print summary statistics
    print(f"\nSummary for {time.value.upper()} Time Profile:")
    print(f"Current Rate: {cur_rate:.2f}%")
    print(f"Target Rate: {target_rate:.2f}%")
    print(f"Volatility: {volatility*100:.1f}%")
    
    return predictions, confidence_intervals, future_dates


if __name__ == '__main__':
    p, ci, fd = predict_bond(Time.SHORT)
    print(p)
    print(ci)
    print(fd)