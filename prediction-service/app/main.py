from fastapi import FastAPI, HTTPException
from .schemas import PredictRequest, PredictResponse, StatsResponse, ModelInfoResponse
from .model_loader import load_model, predict, stats, model_info

app = FastAPI(title='ChurnInsight Prediction Service')

@app.on_event('startup')
def startup_event():
    load_model()

@app.post('/predict', response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    try:
        label, prob = predict(req.dict())
        return PredictResponse(prevision=label, probabilidad=round(prob, 4))
    except Exception as e:
        raise HTTPException(status_code=500, detail='Prediction error')

@app.get('/stats', response_model=StatsResponse)
def stats_endpoint():
    return StatsResponse(**stats())

@app.get('/model-info', response_model=ModelInfoResponse)
def model_info_endpoint():
    info = model_info()
    return ModelInfoResponse(**info)
