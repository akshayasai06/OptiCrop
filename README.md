<img width="2850" height="1558" alt="landing-page" src="https://github.com/user-attachments/assets/c955a268-9d02-413a-b84a-1494206835df" />

---

# OptiCrop - Smart Agricultural Crop Recommendation System

<div align="center">

### Team Details
**JAMPANI AKSHAYA SAI** (Roll No: AP24110011916)  
**Om Keerthana Bhavani** (Roll No: AP24110011229)  
**Rajan Jaiswal** (Roll No: AP24110011202)  
**Sushmanth Chowdary** (Roll No: AP24110011XX)  

</div>

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Repository Structure](#repository-structure)
4. [System Requirements](#system-requirements)
5. [Setup and Execution Instructions](#setup-and-execution-instructions)
6. [API Endpoints](#api-endpoints)
7. [Web Application Interface](#web-application-interface)
8. [Model Training and Evaluation](#model-training-and-evaluation)

---

## Project Overview
OptiCrop is a machine learning-based agricultural recommendation system designed to optimize crop production. By analyzing soil nutrients and environmental parameters, it provides intelligent crop suggestions to improve farming yield, sustainability, and resource utilization.

This repository hosts the modular backend code, machine learning model, unit test suite, and Flask web application built for the Smartbridge Virtual Internship.

---

## Key Features
*   **Data-Driven Crop Recommendations**: Recommends the best crop out of 22 options based on Nitrogen (N), Phosphorous (P), Potassium (K), temperature, humidity, pH level, and rainfall.
*   **Multiple ML Model Evaluation**: Compares Logistic Regression, K-Nearest Neighbors (KNN), Decision Trees, and Random Forests, auto-selecting the best performer (Random Forest achieves 99.55% accuracy).
*   **Modular Architecture**: Clean separation of preprocessing, training, prediction, and presentation concerns.
*   **Dual Mode Flask Server**:
    *   **Interactive Web UI**: A glassmorphic web dashboard styled with Bootstrap 5.
    *   **RESTful JSON API**: Allows frontend developers or mobile apps to query recommendations programmatically.
*   **Extensive Unit Testing**: Validates input bounds, data parsing, and pipeline predictions.
*   **Jupyter Notebook Integration**: Provides detailed exploration, analysis, and visualization.

---

## Repository Structure
```text
optiCrop/
├── .gitignore               # Version control ignore rules
├── README.md                # Project documentation and guide
├── app.py                   # Main Flask server entrypoint (routes and views)
├── requirements.txt         # Python dependencies
├── data/
│   └── Crop_recommendation.csv   # Precision agriculture dataset
├── models/                  # Directory for saved model pickles (locally trained)
│   └── crop_recommendation_model.pkl # Trained Random Forest Pipeline
├── notebooks/
│   └── OptiCrop_Exploration.ipynb # Jupyter notebook for EDA & comparisons
├── static/                  # Static assets for styling and interaction
│   ├── css/
│   │   └── style.css        # Premium glassmorphic styling sheet
│   ├── images/              # Custom background and project graphics
│   │   ├── about-bg.jpg
│   │   ├── find-crop-bg.jpg
│   │   ├── hero-bg.jpg
│   │   └── project.jpg
│   └── js/
│       ├── main.js          # Teammate scripts placeholder
│       └── script.js        # AJAX controller for predictions
├── templates/               # HTML templates for dashboards and other pages
│   ├── home.html            # Main home page
│   ├── about.html           # Team mission and technology stack details
│   └── findyourcrop.html    # Inputs and dynamic prediction page
└── src/
    ├── __init__.py
    ├── model_training.py    # Preprocesses dataset and trains classifiers
    ├── predictor.py         # Handles validation, model loading, and predictions
    └── test_system.py       # Unit & integration testing suite
```

---

## System Requirements
Ensure you have Python 3.10+ installed on your system. No exact version constraints are pinned in the requirements.txt file to allow scikit-learn and pandas to build newer wheels directly from source on modern Python environments (such as Python 3.14+).

---

## Setup and Execution Instructions

### 1. Environment Configuration and Installation
From the root directory of the project, set up a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Model Training and Comparison
To train the machine learning models, compare their accuracies, and serialize the best pipeline:
```bash
python src/model_training.py
```
The script will print accuracy scores for all 4 models and save the top-performing Random Forest pipeline (which includes scaling automatically) to `models/crop_recommendation_model.pkl`.

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
Open http://127.0.0.1:5000 in your browser to interact with the web dashboard.

---

## API Endpoints
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

---

## Web Application Interface

### Landing Page
The home landing page provides an introduction to the optimization engine, features of the platform, and structural parameters examined.

<img width="2850" height="1558" alt="landing-page" src="https://github.com/user-attachments/assets/2572ddc8-8bf7-471a-9d7d-856f40efc9af" />

<img width="2850" height="1554" alt="landing-02" src="https://github.com/user-attachments/assets/a0364145-520b-4714-b9a8-883451a2b74b" />

---

### About Page
The about page highlights the project vision and mission.

<img width="2846" height="1558" alt="about" src="https://github.com/user-attachments/assets/b91a2f93-0a78-4ceb-b72b-611eaf355f44" />

---


### Crop Recommendation Form
The input dashboard on the Find Your Crop page collects agricultural and weather conditions.

<img width="2844" height="1558" alt="crop-recommend" src="https://github.com/user-attachments/assets/e1589d7d-b61a-4a08-8d68-f807ed7ff5cc" />

---

### Prediction Result
The results page displays the classification output and confidence values returned from the model.

<img width="2844" height="1560" alt="prediction-result" src="https://github.com/user-attachments/assets/1e756140-d62c-4821-81e7-78106b41ed74" />


---

## Model Training and Evaluation
The classification logic trains four models (Logistic Regression, KNN, Decision Trees, and Random Forests). The results show that the Random Forest model achieves the highest test set accuracy (99.55%) on the dataset.
<!-- SCREENSHOT 7: Model Performance Comparison plot and classifier evaluation metrics -->
