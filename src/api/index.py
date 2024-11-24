import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from bond_returns import predict_bond
from inflation import predict_inflation
from life_expectancy import predict_life_expectancy 
from govcan_data_manager import Gender, Time


app = Flask(__name__)
CORS(app)

@app.route('/api/get_life_expec', methods=['GET', 'POST'])
def return_life_expec():
    if request.method == 'POST':
        data = request.get_json()
        age = data.get('age')
        gender = data.get('gender')
        
        if gender == 'male':
            gender = Gender.MALE
        else:
            gender = Gender.FEMALE

        return jsonify({"message": f"{int(predict_life_expectancy(age, gender))}"})
    return jsonify({"message": ""})

@app.route('/api/get_inflation', methods=['GET', 'POST'])
def return_inflation():
    if request.method == 'POST':
        data = request.get_json()
        life = data.get('life')
        future_months = life * 12
        
        predictions, _, _ = predict_inflation(future_months=future_months)
        
        
        return jsonify({"predictions": predictions.tolist()})
    return jsonify({"message": ""})

@app.route('/api/get_bond', methods=['GET', 'POST'])
def return_bond():
    if request.method == 'POST':
        data = request.get_json()
        
        life = data.get('life')
        future_months = life * 12
        
        low_preds, _, short_dates = predict_bond(time=Time.SHORT, future_months=future_months)
        med_preds, _, med_dates = predict_bond(time=Time.MED, future_months=future_months)
        long_preds, _, long_dates = predict_bond(time=Time.LONG, future_months=future_months)
        
        return jsonify({"short_predictions": low_preds.tolist(), "short_dates": short_dates.tolist(),
                        "med_predictions": med_preds.tolist(), "med_dates": med_dates.tolist(),
                        "long_predictions": long_preds.tolist(), "long_dates": long_dates.tolist()})
    return jsonify({"message": ""})

@app.route('/api/get_predictions', methods=['GET', 'POST'])
def return_predictions():
    if request.method == 'POST':
        data = request.get_json()
        
        # Data variables setup
        life = data.get('age')
        future_months = life * 12
        
        # Get data from APIs, inflation and bond rate of return
        inflation, _, _ = predict_inflation(future_months=future_months)
        
        low_preds, _, _ = predict_bond(time=Time.SHORT, future_months=future_months)
        med_preds, _, _ = predict_bond(time=Time.MED, future_months=future_months)
        long_preds, _, _ = predict_bond(time=Time.LONG, future_months=future_months)
        
        # Setup for return
        data_len = len(med_preds)
        bonds_per_year = 12
        
        # Create return data format
        pred_data = []
        
        for i in range(data_len):
            year_point = i / bonds_per_year
            
            # format raw values
            short_raw = round(float(low_preds[i]), 2)
            med_raw = round(float(med_preds[i]), 2)
            long_raw = round(float(long_preds[i]), 2)
            inflation_rate = round(float(inflation[i]),2) if i < len(inflation) else 0.0
            
            short_real = round(short_raw - inflation_rate, 2)
            med_real = round(med_raw - inflation_rate, 2)
            long_real = round(long_raw - inflation_rate, 2)
            
            data_point = {
                'year': round(year_point, 2),
                'short': f'{short_real}',
                'med': f'{med_real}',
                'long': f'{long_real}',
                'inflation': f'{inflation_rate}'
            }
            pred_data.append(data_point)

        # get data for finding best investment route
        init_invest = data.get('init_invest')
        
        final_amount, route = get_best_investment_route(predictions=pred_data, invest=init_invest)
        
        print(final_amount)
        print(route)

        return jsonify({"prediction_data": pred_data, "final_amount": final_amount, "route": route})
    return jsonify({"message": "POST REQUEST NEEDED"})


def get_best_investment_route(predictions, invest):
    # yearly averages setup
    years = len(predictions) // 12
    yearly_rates = []
    
    for year in range(years):
        start_idx = year * 12
        end_idx = start_idx + 12
        
        year_avg = {
            'short': sum(float(pred['short']) for pred in predictions[start_idx:end_idx]) / 12,
            'med': sum(float(pred['med']) for pred in predictions[start_idx:end_idx]) / 12,
            'long': sum(float(pred['long']) for pred in predictions[start_idx:end_idx]) / 12,
        }
        yearly_rates.append(year_avg)
    
    # bond parameters
    min_hold = {
        'short': 2,  # 2-3 year bonds
        'med': 5,    # 5-7 year bonds
        'long': 10   # 10+ year bonds
    }
    
    # dp init
    dp = {}
    for year in range(years + 1):
        dp[year] = {
            'short': {'amount': 0, 'prev': None, 'held_years': 0, 'interest_earned': 0},
            'med': {'amount': 0, 'prev': None, 'held_years': 0, 'interest_earned': 0},
            'long': {'amount': 0, 'prev': None, 'held_years': 0, 'interest_earned': 0},
        }
    
    dp[0]['short']['amount'] = invest
    dp[0]['med']['amount'] = invest
    dp[0]['long']['amount'] = invest
    
    for year in range(1, years + 1):
        for cur_bond in ['short', 'med', 'long']:
            max_val = 0
            best_prev = None
            best_held_years = 0
            best_interest = 0
            
            if year - 1 < len(yearly_rates):
                rate = yearly_rates[year-1][cur_bond]
                
                for prev_bond in ['short', 'med', 'long']:
                    prev_val = dp[year-1][prev_bond]['amount']
                    held_years = dp[year-1][prev_bond]['held_years']
                    prev_interest = dp[year-1][prev_bond]['interest_earned']
                    
                    # if staying in same bond
                    if prev_bond == cur_bond:
                        new_held_years = held_years + 1
                        yearly_interest = prev_val * (rate/100) # annual interest payment
                        new_interest = prev_interest + yearly_interest
                        
                        # when bond is mature, give back hold + interest
                        if new_held_years >= min_hold[cur_bond]:
                            new_val = prev_val + yearly_interest
                        else:
                            # Before maturity, just accumulate interest
                            new_val = prev_val
                            
                    # switch bond (at maturity)  
                    else: 
                        if held_years >= min_hold[prev_bond]: #reinvest + give back hold + interest
                            new_val = prev_val + prev_interest
                            new_held_years = 1
                            new_interest = new_val * (rate/100)
                        else:
                            continue
                    
                    if new_val + new_interest > max_val:
                        max_val = new_val
                        best_prev = prev_bond
                        best_held_years = new_held_years
                        best_interest = new_interest
            
            dp[year][cur_bond]['amount'] = max_val
            dp[year][cur_bond]['prev'] = best_prev
            dp[year][cur_bond]['held_years'] = best_held_years
            dp[year][cur_bond]['interest_earned'] = best_interest
    
    # find final amount + interest
    final_amount = 0
    best_final_bond = None
    
    for bond_type in ['short', 'med', 'long']:
        total_value = dp[years][bond_type]['amount'] + dp[years][bond_type]['interest_earned']
        if total_value > final_amount:
            final_amount = total_value
            best_final_bond = bond_type
    
    # reconstruct the route back-front, then reverse
    best_route = []
    cur_bond = best_final_bond
    for year in range(years, 0, -1):
        best_route.append((year, cur_bond))
        cur_bond = dp[year][cur_bond]['prev']
    best_route.reverse()
    
    return final_amount, best_route

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5328, debug=True)