import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_PATH = os.path.join(DATA_DIR, 'churn.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.joblib')

def generate_synthetic_dataset(n=300, random_state=42):
    rng = np.random.default_rng(random_state)
    tiempo = rng.integers(1, 36, size=n)
    retrasos = rng.integers(0, 6, size=n)
    uso = rng.normal(20, 7, size=n).clip(0, None)
    planes = np.array(['Basic', 'Standard', 'Premium'])
    plan = rng.choice(planes, size=n, p=[0.4, 0.4, 0.2])
    plan_factor = np.where(plan == 'Premium', -0.8, np.where(plan == 'Standard', -0.3, 0.0))
    z = 0.03 * (36 - tiempo) + 0.4 * retrasos + (-0.02) * uso + plan_factor + rng.normal(0, 0.5, size=n)
    prob = 1 / (1 + np.exp(-z))
    churn = (rng.random(size=n) < prob).astype(int)
    df = pd.DataFrame({
        'tiempo_contrato_meses': tiempo,
        'retrasos_pago': retrasos,
        'uso_mensual': uso,
        'plan': plan,
        'churn': churn
    })
    return df

def ensure_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        df = generate_synthetic_dataset()
        df.to_csv(CSV_PATH, index=False)

def load_dataset():
    ensure_dataset()
    return pd.read_csv(CSV_PATH)

def build_pipeline():
    numeric_features = ['tiempo_contrato_meses', 'retrasos_pago', 'uso_mensual']
    categorical_features = ['plan']
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    clf = RandomForestClassifier(random_state=42, n_jobs=-1)
    pipe = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', clf)])
    return pipe

def train_and_evaluate():
    df = load_dataset()
    X = df[['tiempo_contrato_meses', 'retrasos_pago', 'uso_mensual', 'plan']]
    y = df['churn']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    base_pipe = build_pipeline()
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [None, 6, 12],
        'classifier__min_samples_leaf': [1, 2],
        'classifier__class_weight': [None, 'balanced']
    }
    grid = GridSearchCV(base_pipe, param_grid=param_grid, cv=5, scoring='f1', n_jobs=-1)
    grid.fit(X_train, y_train)
    model = grid.best_estimator_
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Generar versión basada en timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    version = f"1.0.{timestamp}"
    
    metrics = {
        'accuracy': float(round(acc, 4)),
        'precision': float(round(prec, 4)),
        'recall': float(round(rec, 4)),
        'f1': float(round(f1, 4)),
        'best_params': grid.best_params_,
        'training_date': datetime.now().isoformat(),
        'version': version
    }
    print(metrics)
    joblib.dump(model, MODEL_PATH)
    with open(os.path.join(os.path.dirname(__file__), 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    return MODEL_PATH

if __name__ == '__main__':
    path = train_and_evaluate()
    print({'model_path': path})