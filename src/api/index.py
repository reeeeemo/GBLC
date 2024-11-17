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
        
        predictions, confidence_intervals, _ = predict_inflation(future_months=future_months)
        
        
        return jsonify({"predictions": f"{predictions}", 
                       "confidence": f"{confidence_intervals}"})
    return jsonify({"message": ""})

@app.route('/api/get_bond', methods=['GET', 'POST'])
def return_bond():
    if request.method == 'POST':
        data = request.get_json()
        
        life = data.get('life')
        future_months = life * 12
        
        low_preds, low_confidence, _ = predict_bond(time=Time.SHORT, future_months=future_months)
        med_preds, med_confidence, _ = predict_bond(time=Time.MED, future_months=future_months)
        long_preds, long_confidence, _ = predict_bond(time=Time.LONG, future_months=future_months)
        
        return jsonify({"low_predictions": f"{low_preds}", "low_confidence": f"{low_confidence}",
                        "med_predictions": f"{med_preds}", "med_confidence": f"{med_confidence}",
                        "long_predictions": f"{long_preds}", "long_confidence": f"{long_confidence}"})
    return jsonify({"message": ""})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5328, debug=True)