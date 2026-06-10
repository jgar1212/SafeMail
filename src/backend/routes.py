from fastapi import APIRouter
from backend.services.prediction_service import predict_email

router = APIRouter()

@router.post("/predict")
def predict(data: dict):
    return predict_email(data["text"])
