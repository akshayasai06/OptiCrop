import os
import sys
import unittest

# Add src to path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'src'))

from predictor import CropPredictor
from model_training import load_data, preprocess_and_split, train_and_evaluate_models, save_model

class TestOptiCropSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Ensure model is trained and saved before running tests."""
        cls.data_path = os.path.join(base_dir, "data", "Crop_recommendation.csv")
        cls.model_dir = os.path.join(base_dir, "models")
        cls.model_path = os.path.join(cls.model_dir, "crop_recommendation_model.pkl")
        
        # Train model if it doesn't exist
        if not os.path.exists(cls.model_path):
            print("\n[Test Setup] Model pickle not found. Running training script...")
            df = load_data(cls.data_path)
            X_train, X_test, y_train, y_test, _ = preprocess_and_split(df)
            results, best_model_name, best_pipeline = train_and_evaluate_models(X_train, X_test, y_train, y_test)
            save_model(best_pipeline, cls.model_dir)
            
        cls.predictor = CropPredictor(cls.model_path)

    def test_dataset_exists(self):
        """Test that the crop recommendation dataset file exists."""
        self.assertTrue(os.path.exists(self.data_path), f"Dataset missing at {self.data_path}")

    def test_model_file_exists(self):
        """Test that the pickle model file has been generated."""
        self.assertTrue(os.path.exists(self.model_path), f"Model pickle missing at {self.model_path}")

    def test_valid_prediction(self):
        """Test prediction with realistic parameters for rice."""
        # Typical rice inputs: N=90, P=42, K=43, temp=20.87, humidity=82.00, ph=6.5, rainfall=202.93
        features, errors = self.predictor.validate_inputs(90, 42, 43, 20.87, 82.0, 6.5, 202.9)
        self.assertIsNone(errors)
        self.assertIsNotNone(features)
        
        prediction = self.predictor.predict(features)
        print(f"\n[Test] Rice inputs prediction: {prediction}")
        self.assertIsInstance(prediction, str)
        self.assertTrue(len(prediction) > 0)

    def test_invalid_range_inputs(self):
        """Test that out-of-range inputs trigger validation errors."""
        # Nitrogen -10 (invalid), Humidity 150 (invalid)
        features, errors = self.predictor.validate_inputs(-10, 42, 43, 25.0, 150.0, 6.5, 100.0)
        self.assertIsNotNone(errors)
        self.assertIsNone(features)
        self.assertIn('N', errors)
        self.assertIn('humidity', errors)

    def test_non_numeric_inputs(self):
        """Test that non-numeric inputs trigger validation errors."""
        features, errors = self.predictor.validate_inputs("high", 42, "forty-three", 25.0, 80.0, 6.5, 100.0)
        self.assertIsNotNone(errors)
        self.assertIsNone(features)
        self.assertIn('N', errors)
        self.assertIn('K', errors)

    def test_predict_proba(self):
        """Test that probability predictions are sorted and return valid list."""
        # Run valid check
        features, errors = self.predictor.validate_inputs(90, 42, 43, 20.87, 82.0, 6.5, 202.9)
        self.assertIsNone(errors)
        
        probs = self.predictor.predict_proba(features)
        if probs is not None:
            self.assertIsInstance(probs, list)
            self.assertTrue(len(probs) > 0)
            # Ensure they are sorted descending
            self.assertTrue(probs[0][1] >= probs[-1][1])
            # Ensure probabilities sum to approx 1.0
            sum_prob = sum(prob[1] for prob in probs)
            self.assertAlmostEqual(sum_prob, 1.0, places=2)

if __name__ == '__main__':
    unittest.main()
