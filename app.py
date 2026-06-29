import os
import sys
from flask import Flask, render_template, request, jsonify

# Add src to python path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from predictor import CropPredictor

app = Flask(__name__)

# Initialize predictor lazily
predictor = None

def get_predictor():
    global predictor
    if predictor is None:
        predictor = CropPredictor()
    return predictor

@app.route('/')
@app.route('/home')
def home():
    """Render the main home page."""
    return render_template('home.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/findyourcrop')
def findyourcrop():
    """Render the crop prediction form page."""
    return render_template('findyourcrop.html', inputs=None, errors=None, prediction=None, confidence=None)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request (both HTML form and JSON API)."""
    # Check if request is JSON or Form
    is_json = request.is_json
    
    if is_json:
        data = request.get_json() or {}
    else:
        data = request.form
        
    # Retrieve features
    n = data.get('N')
    p = data.get('P')
    k = data.get('K')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    ph = data.get('ph')
    rainfall = data.get('rainfall')

    # Get predictor instance and validate
    try:
        pred_engine = get_predictor()
    except Exception as e:
        error_msg = f"Model is not trained or loaded: {str(e)}"
        if is_json:
            return jsonify({"status": "error", "message": error_msg}), 500
        else:
            return render_template('findyourcrop.html', inputs=data, errors={"system": error_msg})

    features, errors = pred_engine.validate_inputs(n, p, k, temperature, humidity, ph, rainfall)

    if errors:
        if is_json:
            return jsonify({"status": "fail", "errors": errors}), 400
        else:
            return render_template('findyourcrop.html', inputs=data, errors=errors)

    try:
        # Run prediction
        prediction = pred_engine.predict(features)
        
        # Get crop probabilities for detail/confidence display
        probabilities = pred_engine.predict_proba(features)
        
        # Compute confidence score
        confidence = probabilities[0][1] if probabilities else 1.0
        
        if is_json:
            return jsonify({
                "status": "success",
                "prediction": prediction,
                "probabilities": {crop: float(prob) for crop, prob in probabilities} if probabilities else None,
                "inputs": {
                    "N": float(n),
                    "P": float(p),
                    "K": float(k),
                    "temperature": float(temperature),
                    "humidity": float(humidity),
                    "ph": float(ph),
                    "rainfall": float(rainfall)
                }
            })
        else:
            return render_template(
                'findyourcrop.html',
                prediction=prediction,
                confidence=confidence,
                inputs=data,
                errors=None
            )
            
    except Exception as e:
        error_msg = f"Prediction failed: {str(e)}"
        if is_json:
            return jsonify({"status": "error", "message": error_msg}), 500
        else:
            return render_template('findyourcrop.html', inputs=data, errors={"system": error_msg})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Not Found"}), 404

if __name__ == '__main__':
    # Run Flask development server
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
