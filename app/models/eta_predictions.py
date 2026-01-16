from sqlalchemy import Column, Integer, Float, DateTime,String
from sqlalchemy.sql import func
from app.db.session import Base

class PredictionHistory(Base):
    __tablename__ = "eta_predictions"

    id = Column(Integer, primary_key=True, index=True)

    passenger_count = Column(Integer, nullable=False)
    trip_distance = Column(Float, nullable=False)
    ratecode_id = Column(Integer, nullable=True)  

    fare_amount = Column(Float, nullable=False)
    tip_amount = Column(Float, nullable=True)
    tolls_amount = Column(Float, nullable=True)
    airport_fee = Column(Float, nullable=True)

    trip_duration = Column(Float, nullable=False)
    pickup_hour = Column(Integer, nullable=False)

    predicted_duration = Column(Float, nullable=False)
    model_version = Column(String(20), nullable=False)
    username = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
