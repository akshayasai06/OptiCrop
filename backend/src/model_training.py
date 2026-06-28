import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

# Import algorithms
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

def load_data(file_path):
    """Load dataset from the CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at: {file_path}")
    print(f"Loading dataset from {file_path}...")
    df = pd.read_csv(file_path)
    return df

def preprocess_and_split(df):
    """Split data into features and target, and train/test sets."""
    # Features are N, P, K, temperature, humidity, ph, rainfall
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    # Check for missing values
    missing_vals = X.isnull().sum().sum()
    if missing_vals > 0:
        print(f"Warning: Found {missing_vals} missing values. Filling with mean.")
        X = X.fillna(X.mean())
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    return X_train, X_test, y_train, y_test, X.columns.tolist()

def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """Train multiple classifiers using pipeline (with StandardScaler) and compare them."""
    # Define models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    results = {}
    best_acc = 0.0
    best_pipeline = None
    best_model_name = ""
    
    print("\n--- Training and Evaluating Models ---")
    for name, model in models.items():
        # Using a pipeline with scaling is good practice, especially for KNN and Logistic Regression
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', model)
        ])
        
        # Fit model
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted')
        rec = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        results[name] = {
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "Pipeline": pipeline
        }
        
        print(f"{name:20} -> Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1-Score: {f1:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_pipeline = pipeline
            best_model_name = name
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_acc:.4f}")
    return results, best_model_name, best_pipeline

def save_model(pipeline, model_dir, model_name="crop_recommendation_model.pkl"):
    """Serialize the trained pipeline model to a pickle file."""
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, model_name)
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"\nSaved best model pipeline to {model_path}")
    return model_path

if __name__ == "__main__":
    # Define paths relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "Crop_recommendation.csv")
    model_dir = os.path.join(base_dir, "models")
    
    df = load_data(data_path)
    X_train, X_test, y_train, y_test, feature_names = preprocess_and_split(df)
    
    results, best_model_name, best_pipeline = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Save the best model
    save_model(best_pipeline, model_dir)
