import os
import joblib
import hashlib
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

_here = os.path.dirname(__file__)
_svc_dir = os.path.dirname(_here)
_root_dir = os.path.dirname(_svc_dir)
_env_model_path = os.environ.get('MODEL_PATH')
_default_paths = [
    os.path.join(_root_dir, 'data-science', 'model.joblib'),
    os.path.join(_svc_dir, 'model.joblib')
]
MODEL_PATH = _env_model_path if _env_model_path else _default_paths[0]

_model = None
_model_path = None
_predictions_count = 0

def _generate_synthetic(n=300, random_state=42):
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

def _build_pipeline():
    numeric = ['tiempo_contrato_meses', 'retrasos_pago', 'uso_mensual']
    categorical = ['plan']
    pre = ColumnTransformer([
        ('num', StandardScaler(), numeric),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
    ])
    clf = LogisticRegression(max_iter=1000, solver='liblinear')
    return Pipeline([('preprocessor', pre), ('classifier', clf)])

def _resolve_model_path():
    if _env_model_path and os.path.exists(_env_model_path):
        return _env_model_path
    existing = [p for p in _default_paths if os.path.exists(p)]
    if existing:
        latest = max(existing, key=lambda p: os.path.getmtime(p))
        return latest
    return MODEL_PATH

def ensure_model():
    target_path = _resolve_model_path()
    if not os.path.exists(target_path):
        df = _generate_synthetic()
        X = df[['tiempo_contrato_meses', 'retrasos_pago', 'uso_mensual', 'plan']]
        y = df['churn']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        model = _build_pipeline()
        model.fit(X_train, y_train)
        joblib.dump(model, target_path)

def load_model():
    global _model
    global _model_path
    ensure_model()
    path = _resolve_model_path()
    _model = joblib.load(path)
    _model_path = path

def predict(payload):
    global _predictions_count
    if _model is None:
        load_model()
    X = pd.DataFrame([payload])
    proba = _model.predict_proba(X)[0]
    classes = list(_model.classes_)
    idx = classes.index(1) if 1 in classes else 0
    p_cancel = float(proba[idx])
    pred_label = 'Va a cancelar' if p_cancel >= 0.5 else 'Va a continuar'
    _predictions_count += 1
    return pred_label, p_cancel

def stats():
    return {'predictions_count': _predictions_count}

def _calculate_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def model_info():
    path = _model_path if _model_path else _resolve_model_path()
    metrics_data = None
    
    candidates = [
        os.path.join(os.path.dirname(path), 'metrics.json'),
        os.path.join(_root_dir, 'data-science', 'metrics.json')
    ]
    
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                break
            except Exception:
                metrics_data = None
                break
    
    info = {
        'model_path': path,
        'model_hash': _calculate_file_hash(path),
        'best_params': None,
        'metrics': None,
        'training_date': None,
        'version': None
    }

    if metrics_data:
        info['best_params'] = metrics_data.get('best_params')
        # Filter out best_params from metrics to avoid duplication if desired, 
        # but user asked for "metrics completas... incluyendo métricas"
        # The metrics.json has flat structure mostly, so we can separate them if we want
        # or just pass the whole thing. 
        # Let's separate standard metrics from metadata
        
        std_metrics = {k: v for k, v in metrics_data.items() 
                      if k not in ['best_params', 'training_date', 'version']}
        
        info['metrics'] = std_metrics
        info['training_date'] = metrics_data.get('training_date')
        info['version'] = metrics_data.get('version')
        
    return info
