# OptiCrop - Smart Agricultural Crop Recommendation System

OptiCrop is a machine learning-based agricultural recommendation system designed to optimize crop production. By analyzing soil nutrients and environmental parameters, it provides intelligent crop suggestions to improve farming yield, sustainability, and resource utilization.

This repository hosts the modular backend code, machine learning model, unit test suite, and Flask web application built for the Smartbridge Virtual Internship.

---

## 🚀 Key Features

*   **Data-Driven Crop Recommendations**: Recommends the best crop out of 22 options based on Nitrogen (N), Phosphorous (P), Potassium (K), temperature, humidity, pH level, and rainfall.
*   **Multiple ML Model Evaluation**: Compares Logistic Regression, K-Nearest Neighbors (KNN), Decision Trees, and Random Forests, auto-selecting the best performer (Random Forest achieves **99.55% accuracy**).
*   **Modular Architecture**: Clean separation of preprocessing, training, prediction, and presentation concerns.
*   **Dual Mode Flask Server**:
    *   **Interactive Web UI**: A glassmorphic web dashboard styled with Bootstrap 5.
    *   **RESTful JSON API**: Allows frontend developers or mobile apps to query recommendations programmatically.
*   **Extensive Unit Testing**: Validates input bounds, data parsing, and pipeline predictions.
*   **Jupyter Notebook Integration**: Provides detailed exploration, analysis, and visualization.

---

## 📁 Repository Structure

```text
optiCrop/
├── .gitignore               # Ignored files (venv, caches, task trackers, model binaries)
├── README.md                # Project documentation and guide
├── tasks.md                 # Local internship checklist (git-ignored)
└── backend/
    ├── app.py               # Main Flask server entrypoint (routes and views)
    ├── requirements.txt     # Python dependencies
    ├── data/
    │   └── Crop_recommendation.csv   # Precision agriculture dataset
    ├── models/
    │   └── crop_recommendation_model.pkl # Best trained model pipeline (ignored from Git)
    ├── notebooks/
    │   └── OptiCrop_Exploration.ipynb # Jupyter notebook for EDA & comparisons
    ├── static/
    │   └── css/
    │       └── style.css    # Premium glassmorphic styling sheet
    ├── templates/
    │   ├── base.html        # Main layouts & Bootstrap 5 inclusion
    │   ├── index.html       # Responsive input forms for agricultural metrics
    │   └── result.html      # Prediction output with match likelihood gauges
    └── src/
        ├── __init__.py
        ├── model_training.py # Preprocesses dataset and trains classifiers
        ├── predictor.py     # Handles validation, model loading, and predictions
        └── test_system.py   # Unit & integration testing suite
```

---

## 🛠️ Setup & Execution Instructions

Ensure you have **Python 3.10+** installed on your system.

### 1. Environment Configuration & Installation

From the root directory, navigate into the `backend` folder, set up a virtual environment, and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Model Training & Comparison

To train the machine learning models, compare their accuracies, and serialize the best pipeline:

```bash
python src/model_training.py
```
*The script will print accuracy scores for all 4 models and save the top-performing **Random Forest pipeline** (which includes scaling automatically) to `models/crop_recommendation_model.pkl`.*

### 3. Run Unit and Integration Tests

To run the full test suite and verify system components:

```bash
python src/test_system.py
```

### 4. Launch the Web Application

To run the Flask development server:

```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser to interact with the web dashboard.

---

## 🔌 API Endpoints (For Frontend Developers)

The Flask server supports raw JSON requests in addition to standard form submissions.

### Post Recommendation Query
*   **URL**: `/predict`
*   **Method**: `POST`
*   **Headers**: `Content-Type: application/json`
*   **Request Body**:
    ```json
    {
      "N": 90,
      "P": 42,
      "K": 43,
      "temperature": 20.87,
      "humidity": 82.0,
      "ph": 6.5,
      "rainfall": 202.9
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "status": "success",
      "prediction": "rice",
      "probabilities": {
        "rice": 0.98,
        "maize": 0.02
      },
      "inputs": {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "temperature": 20.87,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
      }
    }
    ```
*   **Validation Error Response (400 Bad Request)**:
    ```json
    {
      "status": "fail",
      "errors": {
        "humidity": "Must be between 0.0 and 100.0."
      }
    }
    ```
