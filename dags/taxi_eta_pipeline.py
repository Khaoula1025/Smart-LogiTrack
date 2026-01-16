from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, hour, dayofweek, month, dayofmonth, unix_timestamp, 
    round as spark_round, when
)
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer, OneHotEncoder
from pyspark.ml.regression import RandomForestRegressor, GBTRegressor, LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator

# Configuration
DB_HOST = os.getenv('SILVER_DB_HOST', 'localhost')
DB_PORT = os.getenv('SILVER_DB_PORT', '5432')
DB_NAME = os.getenv('SILVER_DB_NAME', 'silver_data')
DB_USER = os.getenv('SILVER_DB_USER', 'silver_user')
DB_PASSWORD = os.getenv('SILVER_DB_PASSWORD', 'silver_pass123')

JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
BRONZE_PATH = "/data/bronze/dataset.parquet"
MODEL_PATH = "/notebooks/models/GradientBoostedTrees_model"

def get_spark():
    return SparkSession.builder \
        .appName("TaxiETA") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.5.1") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

def process_data(**context):
    """Process bronze data and save to silver database"""
    spark = get_spark()
    try:
        # Load data from bronze
        print(f"📂 Loading data from {BRONZE_PATH}")
        df = spark.read.parquet(BRONZE_PATH)
        rows_before = df.count()
        print(f"✅ Loaded {rows_before:,} rows")
        
        # Create target column: trip_duration in minutes
        print("🎯 Creating trip_duration target column...")
        df_silver = df.withColumn(
            'trip_duration',
            spark_round(
                (unix_timestamp('tpep_dropoff_datetime') - 
                 unix_timestamp('tpep_pickup_datetime')) / 60,
                2
            )
        )
        
        # Data cleaning with filters
        print("🧹 Cleaning data with filters...")
        df_silver = df_silver.filter(
            (col("trip_duration") > 1) &
            (col("trip_duration") < 120) &
            (col("trip_distance") > 0.1) &
            (col("trip_distance") < 100) &
            (col("passenger_count") >= 1) &
            (col("fare_amount") > 0) &
            (col("total_amount") > 0) &
            (col("total_amount") < 500)
        )
        
        # Remove outliers using IQR method on trip_duration
        print("📊 Removing outliers using IQR method...")
        duration_stats = df_silver.approxQuantile('trip_duration', [0.25, 0.75], 0.01)
        Q1, Q3 = duration_stats[0], duration_stats[1]
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df_silver = df_silver.filter(
            (col('trip_duration') >= lower_bound) &
            (col('trip_duration') <= upper_bound)
        )
        # Feature engineering: Extract time-based features
        print("⚙️ Engineering time-based features...")
        df_silver = df_silver.withColumn("pickup_hour", hour(col("tpep_pickup_datetime"))) \
                             .withColumn("pickup_day_of_week", dayofweek(col("tpep_pickup_datetime"))) \
                             .withColumn("pickup_day", dayofmonth(col("tpep_pickup_datetime"))) \
                             .withColumn("pickup_month", month(col("tpep_pickup_datetime")))
        
        # Time of day categories
        df_silver = df_silver.withColumn(
            "time_of_day",
            when((col("pickup_hour") >= 6) & (col("pickup_hour") < 12), "Morning")
            .when((col("pickup_hour") >= 12) & (col("pickup_hour") < 17), "Afternoon")
            .when((col("pickup_hour") >= 17) & (col("pickup_hour") < 21), "Evening")
            .otherwise("Night")
        )
        
        # Weekend flag
        df_silver = df_silver.withColumn(
            "is_weekend",
            when(col("pickup_day_of_week").isin([1, 7]), 1).otherwise(0)
        )
        
        # Rush hour flag
        df_silver = df_silver.withColumn(
            "is_rush_hour",
            when(
                ((col("pickup_hour") >= 7) & (col("pickup_hour") <= 9)) |
                ((col("pickup_hour") >= 17) & (col("pickup_hour") <= 19)),
                1
            ).otherwise(0)
        )
        
        # Optimize partitions for writing
        print("🔄 Optimizing partitions for database write...")
        df_silver_optimized = df_silver.repartition(20)
        
        # Write to PostgreSQL
        print("💾 Writing to PostgreSQL (silver_table)...")
        df_silver_optimized.write \
            .format("jdbc") \
            .option("url", JDBC_URL) \
            .option("dbtable", "silver_table") \
            .option("user", DB_USER) \
            .option("password", DB_PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .option("batchsize", "100000") \
            .mode("overwrite") \
            .save()
        
        # Verify
        df_verify = spark.read.format("jdbc") \
            .option("url", JDBC_URL) \
            .option("dbtable", "silver_table") \
            .option("user", DB_USER) \
            .option("password", DB_PASSWORD) \
            .load()
        
        print(f"✅ Successfully saved {df_verify.count():,} rows to PostgreSQL")
        
    finally:
        spark.stop()

def train_model(**context):
    """Train ML models on silver data"""
    spark = get_spark()
    try:
        # Load data from silver database
        print("📂 Loading data from silver_table...")
        df = spark.read.format("jdbc") \
            .option("url", JDBC_URL) \
            .option("dbtable", "silver_table") \
            .option("user", DB_USER) \
            .option("password", DB_PASSWORD) \
            .load()
        
        print(f"✅ Loaded {df.count():,} rows from silver database")
        
        # Drop columns not needed for training
        columns_to_drop = [
            'VendorID', 'store_and_fwd_flag', 'total_amount', 'extra', 'mta_tax',
            'congestion_surcharge', 'improvement_surcharge', 'is_rush_hour',
            'time_of_day', 'payment_type', 'pickup_day', 'pickup_day_of_week',
            'PULocationID', 'DOLocationID', 'pickup_month', 'is_weekend',
            'tpep_pickup_datetime', 'tpep_dropoff_datetime'
        ]
        
        # Filter out columns that exist
        columns_to_drop = [c for c in columns_to_drop if c in df.columns]
        df = df.drop(*columns_to_drop)
        
        # Add cbd_congestion_fee to drop list if it exists
        if 'cbd_congestion_fee' in df.columns:
            df = df.drop('cbd_congestion_fee')
        
        print(f"📋 Remaining columns: {df.columns}")
        
        # Filter null values in target
        df = df.filter(col("trip_duration").isNotNull())
        
        # Configuration
        numerical_features = [
            'passenger_count', 'trip_distance', 'fare_amount',
            'tip_amount', 'tolls_amount', 'Airport_fee', 'pickup_hour'
        ]
        # Filter features that actually exist
        numerical_features = [f for f in numerical_features if f in df.columns]
        
        categorical_features = ['RatecodeID'] if 'RatecodeID' in df.columns else []
        target_column = 'trip_duration'
        
        print(f"\n🎯 FEATURE CONFIGURATION:")
        print(f"   Numerical: {len(numerical_features)} features - {numerical_features}")
        print(f"   Categorical: {len(categorical_features)} features - {categorical_features}")
        print(f"   Target: {target_column}")
        
        # Train/test split
        train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
        train_df = train_df.cache()
        test_df = test_df.cache()      
        # Create preprocessing stages
        def create_preprocessing_stages():
            stages = []
            
            if categorical_features:
                # Encode categorical features
                indexer = StringIndexer(
                    inputCol='RatecodeID',
                    outputCol='RatecodeID_indexed',
                    handleInvalid='keep'
                )
                stages.append(indexer)
                
                encoder = OneHotEncoder(
                    inputCols=['RatecodeID_indexed'],
                    outputCols=['RatecodeID_encoded'],
                    dropLast=True
                )
                stages.append(encoder)
            
            # Assemble numerical features
            numerical_assembler = VectorAssembler(
                inputCols=numerical_features,
                outputCol='numerical_features_vec',
                handleInvalid='skip'
            )
            stages.append(numerical_assembler)
            
            # Scale numerical features
            scaler = StandardScaler(
                inputCol='numerical_features_vec',
                outputCol='numerical_features_scaled',
                withMean=True,
                withStd=True
            )
            stages.append(scaler)
            
            # Final assembly
            final_input_cols = ['numerical_features_scaled']
            if categorical_features:
                final_input_cols.append('RatecodeID_encoded')
            
            final_assembler = VectorAssembler(
                inputCols=final_input_cols,
                outputCol='features',
                handleInvalid='skip'
            )
            stages.append(final_assembler)
            
            return stages
        
        # Define models
        models = {
            'RandomForest': RandomForestRegressor(
                featuresCol='features',
                labelCol=target_column,
                predictionCol='prediction',
                numTrees=100,
                maxDepth=10,
                minInstancesPerNode=5,
                subsamplingRate=0.8,
                featureSubsetStrategy='sqrt',
                seed=42
            ),
            'GradientBoostedTrees': GBTRegressor(
                featuresCol='features',
                labelCol=target_column,
                predictionCol='prediction',
                maxIter=100,
                maxDepth=8,
                stepSize=0.1,
                subsamplingRate=0.8,
                featureSubsetStrategy='sqrt',
                seed=42
            ),
            'LinearRegression': LinearRegression(
                featuresCol='features',
                labelCol=target_column,
                predictionCol='prediction',
                maxIter=100,
                regParam=0.1,
                elasticNetParam=0.5,
                standardization=False
            )
        }
        
        print(f"\n🤖 Training {len(models)} models...")
        
        # Train and evaluate models
        results = {}
        best_rmse = float('inf')
        best_model_name = None
        best_model = None
        
        for model_name, model in models.items():
            print(f"\n{'='*70}")
            print(f"🚀 TRAINING: {model_name}")
            print(f"{'='*70}")
            
            # Create pipeline
            preprocessing_stages = create_preprocessing_stages()
            pipeline = Pipeline(stages=preprocessing_stages + [model])
            
            # Train
            start_time = datetime.now()
            trained_model = pipeline.fit(train_df)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Predict
            predictions = trained_model.transform(test_df)
            
            # Evaluate
            evaluator_rmse = RegressionEvaluator(
                labelCol=target_column,
                predictionCol='prediction',
                metricName='rmse'
            )
            evaluator_mae = RegressionEvaluator(
                labelCol=target_column,
                predictionCol='prediction',
                metricName='mae'
            )
            evaluator_r2 = RegressionEvaluator(
                labelCol=target_column,
                predictionCol='prediction',
                metricName='r2'
            )
            
            rmse = evaluator_rmse.evaluate(predictions)
            mae = evaluator_mae.evaluate(predictions)
            r2 = evaluator_r2.evaluate(predictions)
            
            print(f"\n📈 METRICS:")
            print(f"   RMSE: {rmse:.2f} minutes")
            print(f"   MAE:  {mae:.2f} minutes")
            print(f"   R²:   {r2:.4f}")
            print(f"   Training time: {training_time:.2f}s")
            
            results[model_name] = {
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'training_time': training_time
            }
            
            # Track best model
            if rmse < best_rmse:
                best_rmse = rmse
                best_model_name = model_name
                best_model = trained_model
        
        # Print comparison
        print(f"\n{'='*70}")
        print("📊 MODEL COMPARISON")
        print(f"{'='*70}")
        for name, metrics in sorted(results.items(), key=lambda x: x[1]['rmse']):
            print(f"\n{name}:")
            print(f"   RMSE: {metrics['rmse']:.2f} min")
            print(f"   MAE:  {metrics['mae']:.2f} min")
            print(f"   R²:   {metrics['r2']:.4f}")
            print(f"   Time: {metrics['training_time']:.2f}s")
        
        print(f"\n🏆 BEST MODEL: {best_model_name} (RMSE: {best_rmse:.2f} min)")
        
        # Save best model
        Path(MODEL_PATH).mkdir(parents=True, exist_ok=True)
        model_save_path = f"{MODEL_PATH}/{best_model_name}_model"
        best_model.write().overwrite().save(model_save_path)
        print(f"✅ Model saved to {model_save_path}")
        
    finally:
        spark.stop()

# DAG definition
default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'taxi_eta_pipeline',
    default_args=default_args,
    description='Taxi ETA prediction pipeline with silver processing',
    schedule_interval='@daily',
    catchup=False,
    tags=['taxi', 'ml', 'silver'],
) as dag:
    
    process = PythonOperator(
        task_id='process_to_silver',
        python_callable=process_data
    )
    
    train = PythonOperator(
        task_id='train_models',
        python_callable=train_model
    )
    
    process >> train