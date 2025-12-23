from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

class PredictRequest(BaseModel):
    tiempo_contrato_meses: int = Field(..., ge=0)
    retrasos_pago: int = Field(..., ge=0)
    uso_mensual: float = Field(..., ge=0)
    plan: Literal['Basic', 'Standard', 'Premium']

class PredictResponse(BaseModel):
    prevision: str
    probabilidad: float

class StatsResponse(BaseModel):
    predictions_count: int

class ModelInfoResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_path: str
    best_params: Optional[dict] = None
    metrics: Optional[dict] = None
    training_date: Optional[str] = None
    version: Optional[str] = None
    model_hash: Optional[str] = None