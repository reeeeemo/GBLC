import numpy as np
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime
from govcan_data_manager import Gender, get_life_expectancy_data, GOMPERTZ_MAX, HealthFactors

def polynomial_features(X, degree=2):
    X_poly = np.ones((X.shape[0], degree + 1))
    for i in range(1, degree + 1):
        X_poly[:, i] = X[:, 0] ** i
    return X_poly

def linear_regression(X, y, weights=None):
    if weights is None:
        weights = np.ones(len(y))
        
    W = np.diag(weights)
    theta = np.linalg.inv(X.T.dot(W).dot(X)).dot(X.T).dot(W).dot(y)
    return theta

def predict_with_coeffs(X, coeffs):
    return X.dot(coeffs)

def predict_life_expectancy(age=0, gender=Gender.BOTH, health_factors=None, years_back=20):
    '''
    Predict life expectancy based on age, gender, and health factors
    
    age (int): current age of the person
    gender (Gender)
    health_factors (HealthFactors)
    years_back (int): Years of historical data to use
    '''
    # Get Life Expectancy Data
    dates, values = get_life_expectancy_data(gender, years_back)
    
    X = np.array(dates).reshape(-1, 1)
    y = np.array(values)
    
    # Create Weights (reduce COVID impact)
    weights = np.ones(len(dates))
    covid_years = [2020, 2021, 2022]
    for i, year in enumerate(dates):
        if year in covid_years:
            weights[i] = 0.05 # 5%
        
    # polynomial features
    X_poly = polynomial_features(X, degree=2)
    
    coeffs = linear_regression(X_poly, y, weights)
    
    # Make base prediction
    current_year = datetime.now().year
    X_future = polynomial_features(np.array([[current_year]]), degree=2)
    base_prediction = predict_with_coeffs(X_future, coeffs=coeffs)[0]
    
    # SCIKIT IMPLEMENTATION
    #poly = PolynomialFeatures(degree=2)
    #X_poly = poly.fit_transform(X)
    #model = LinearRegression()
    #model.fit(X_poly, y, sample_weight=weights)
    #X_future = poly.transform(np.array([[current_year]])) 
    #base_prediction = model.predict(X_future)[0]
    
    # Adjust for age
    if age > 0:
        remaining_years = base_prediction - age
    else:
        remaining_years = base_prediction
        
    # Adjust for health factors
    if health_factors:
        health_impact = health_factors.calculate_health_impact()
        remaining_years += health_impact
    
    # Gender-specific adjustments
    if gender == Gender.FEMALE:
        remaining_years += 2
    elif gender == Gender.MALE:
        remaining_years -= 2
    
    final_prediction = max(0, min(remaining_years, GOMPERTZ_MAX)) # no 0, and only max possible age
    
    return final_prediction

