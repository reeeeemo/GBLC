import numpy as np
from govcan_data_manager import get_inflation_data


def predict_inflation(future_months=60, target_rate=2.0):
    """
    Predict future inflation rates 
    
    Target-based monte carlo approch: prediction = base + seasonal + random variation
    
    sim method that combines known/target and random elements to predict future vals while converging to our known target
    
    base = weighted avg btwn current rate and our target rate (cur rate converge to target (2.0))
    seasonal = cyclical pattern for seasonal variations (sine wave!)
    random_variation = normal distribution noise (random variations!)
    """
    # Get historical data
    dates, values = get_inflation_data()
    
    cur_rate = values[-1]
    
    # future dates
    last_date = dates[-1]
    future_dates = np.array([last_date + (30*24*60*60*i) for i in range(1, future_months+1)])
    
    # predictions array
    predictions = np.zeros(future_months)
    confidence_intervals = np.zeros((future_months, 2))
    
    # prediction params
    convergence_period = 24 # 2 years to converge to target
    year_cycle = 12
    
    # Store current target rate
    current_target = target_rate
    
    # confidence interval parameters
    base_uncertainty = 0.25
    max_uncertainty = 0.75
    uncertainty_growth = 0.1
    
    for i in range(future_months): # monte carlo sim
        year = i // 12
        month = i % 12
        
        # base prediction from cur rate
        if i < convergence_period:
            weight = (convergence_period - i) / convergence_period
            base_prediction = cur_rate * weight + current_target * (1 - weight)
        else:
            # after convergence, use dynamic targets
            if i % 24 == 0:
                current_target = current_target + np.random.normal(0, 0.2)
                current_target = max(1.0, min(3.0, current_target)) # btwn 1-3%
                
            base_prediction = current_target
            
        # seasonal variation
        seasonal = 0.1 * np.sin(2 * np.pi * month / year_cycle)
        
        # random variation (more pronounced in early months)
        time_weight = min(1.0, i / 24)
        random_variation = np.random.normal(0, 0.2 * (1 - time_weight))
        
        # Combine all components
        predictions[i] = base_prediction + seasonal + random_variation
        
        # Ensure prediction doesn't go below 0
        predictions[i] = max(0.1, predictions[i])
        
        # calc our new confidence intervals
        years_out = i / 12
        current_uncertainty = min(max_uncertainty, 
                                base_uncertainty + (uncertainty_growth * years_out))
        
        confidence_intervals[i] = [
            max(0.5, predictions[i] - current_uncertainty),
            min(4.0, predictions[i] + current_uncertainty)
        ]
        
    # Print key predictions
    print("\nKey Predictions:")
    years = [2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033]
    for year in years:
        year_start_idx = (year - 2024) * 12
        year_end_idx = year_start_idx + 11
        if year_end_idx < len(predictions):  # Make sure we don't go out of bounds
            year_avg = np.mean(predictions[year_start_idx:year_end_idx+1])
            year_min = np.min(predictions[year_start_idx:year_end_idx+1])
            year_max = np.max(predictions[year_start_idx:year_end_idx+1])
            print(f"\n{year}:")
            print(f"  Average: {year_avg:.2f}%")
            print(f"  Range: {year_min:.2f}% - {year_max:.2f}%")
            print(f"  Confidence: {np.mean(confidence_intervals[year_start_idx:year_end_idx+1], axis=0)}")

    return predictions, confidence_intervals, future_dates
    
