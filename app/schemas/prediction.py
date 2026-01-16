from pydantic import BaseModel, Field
class TripFeatures(BaseModel):
    passenger_count: int = Field(..., ge=1, le=6, description="Nombre de passagers (1-6)")
    trip_distance: float = Field(..., gt=0, le=200, description="Distance en miles")
    RatecodeID: int = Field(..., ge=1, le=6, description="Code tarif (1-6)")
    fare_amount: float = Field(..., ge=0, description="Tarif de base")
    tip_amount: float = Field(0, ge=0, description="Pourboire")
    tolls_amount: float = Field(0, ge=0, description="Péages")
    Airport_fee: float = Field(0, ge=0, description="Frais d'aéroport")
    pickup_hour: int = Field(..., ge=0, le=23, description="Heure de départ (0-23)")

class PredictionResponse(BaseModel):
    estimated_duration: float
    timestamp: str
    model_version: str

class AvgDurationByHour(BaseModel):
    pickup_hour: int
    avg_duration: float
    total_trips: int

class PaymentAnalysis(BaseModel):
    payment_type: int
    total_trips: int
    avg_duration: float
    avg_fare: float