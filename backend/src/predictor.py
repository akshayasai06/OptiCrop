import os
import pickle
import numpy as np

class CropPredictor:
    def __init__(self, model_path=None):
        """Initialize the predictor by loading the serialized model pipeline."""
        if model_path is None:
            # Resolve path relative to this script
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "crop_recommendation_model.pkl")
            
        self.model_path = model_path
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load the model pipeline from the pickle file."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found at: {self.model_path}. "
                "Please run model training first to generate it."
            )
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("Model loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Error loading model from {self.model_path}: {e}")

    def validate_inputs(self, n, p, k, temperature, humidity, ph, rainfall):
        """
        Validate input parameters for the crop prediction model.
        Returns a dict of errors if validation fails, otherwise returns None.
        """
        errors = {}
        
        # Helper to check floats
        def check_float(val, name, min_val, max_val):
            try:
                f_val = float(val)
                if not (min_val <= f_val <= max_val):
                    errors[name] = f"Must be between {min_val} and {max_val}."
                return f_val
            except (ValueError, TypeError):
                errors[name] = "Must be a valid number."
                return None

        # Soil Nitrogen (N): typically 0-150
        n_val = check_float(n, 'N', 0.0, 200.0)
        # Soil Phosphorus (P): typically 0-150
        p_val = check_float(p, 'P', 0.0, 200.0)
        # Soil Potassium (K): typically 0-250
        k_val = check_float(k, 'K', 0.0, 300.0)
        # Temperature: typically 0-60 C
        temp_val = check_float(temperature, 'temperature', -10.0, 60.0)
        # Humidity: typically 0-100%
        hum_val = check_float(humidity, 'humidity', 0.0, 100.0)
        # pH: typically 0-14
        ph_val = check_float(ph, 'ph', 0.0, 14.0)
        # Rainfall: typically 0-500mm
        rain_val = check_float(rainfall, 'rainfall', 0.0, 1000.0)
        
        if errors:
            return None, errors
            
        validated_data = [n_val, p_val, k_val, temp_val, hum_val, ph_val, rain_val]
        return validated_data, None

    def predict(self, features):
        """
        Predict the recommended crop based on input features.
        :param features: List of floats: [N, P, K, temperature, humidity, ph, rainfall]
        :return: String (predicted crop label)
        """
        if self.model is None:
            self._load_model()
            
        # Reshape for single prediction [1, 7]
        features_arr = np.array(features).reshape(1, -1)
        
        # Predict using the loaded pipeline (handles scaling automatically)
        prediction = self.model.predict(features_arr)
        
        # Some models return array of classes, get the first element
        return str(prediction[0])
        
    def predict_proba(self, features):
        """
        Predict probability distribution across all crops.
        Returns a sorted list of tuples (crop, probability) in descending order.
        """
        if self.model is None:
            self._load_model()
            
        features_arr = np.array(features).reshape(1, -1)
        
        # If the classifier in pipeline supports predict_proba
        try:
            probabilities = self.model.predict_proba(features_arr)[0]
            classes = self.model.classes_
            crop_probs = list(zip(classes, probabilities))
            crop_probs.sort(key=lambda x: x[1], reverse=True)
            return crop_probs
        except AttributeError:
            return None
