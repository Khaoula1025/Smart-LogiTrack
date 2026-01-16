from fastapi import FastAPI,APIRouter
from app.db.session import Base,engine
from app.api.v1.endpoints.auth import authRouter 
from app.api.v1.endpoints.prediction import predictionRouter 
from app.api.v1.endpoints.prediction import predictionRouter 
from app.api.v1.endpoints.analytics import analyticsRouter
app=FastAPI(
    description="taxi_eta_pridiction "
)
Base.metadata.create_all(bind=engine)
app.include_router(authRouter)
app.include_router(predictionRouter)
app.include_router(analyticsRouter)

