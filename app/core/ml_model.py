from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from typing import Optional

# Variables globales
spark: Optional[SparkSession] = None
model: Optional[PipelineModel] = None
MODEL_VERSION: str = "v1.0"
FEATURES = [
    'passenger_count',
    'trip_distance',
    'RatecodeID',
    'fare_amount',
    'tip_amount',
    'tolls_amount',
    'Airport_fee',
    'trip_duration',
    'pickup_hour'
]
