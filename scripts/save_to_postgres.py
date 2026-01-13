from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import os

# Create Spark Session
spark = SparkSession.builder \
    .appName("SaveSilverDataToPostgres") \
    .config("spark.jars", "/home/user/spark_libs/postgresql-42.6.0.jar") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

print("✅ Spark session created successfully")

# PostgreSQL connection details
jdbc_url = "jdbc:postgresql://localhost:5432/silver_data"
connection_properties = {
    "user": "silver_user",
    "password": "silver_pass123",
    "driver": "org.postgresql.Driver"
}

# Example: Load your silver data
# Replace this with your actual data source
print("📊 Loading data...")

# Option A: If reading from file (CSV, Parquet, etc.)
# df = spark.read.parquet("/path/to/your/silver/data.parquet")

# Option B: If reading from Delta Lake
# df = spark.read.format("delta").load("/path/to/delta/table")

# Option C: Sample data for testing
data = [
    (1, "Product A", 100.50, "2024-01-01"),
    (2, "Product B", 200.75, "2024-01-02"),
    (3, "Product C", 150.25, "2024-01-03")
]
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("product_name", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("date", StringType(), True)
])
df = spark.createDataFrame(data, schema)

print(f"📈 Data loaded: {df.count()} rows")
df.show(5)

# Write to PostgreSQL
print("💾 Writing to PostgreSQL...")

df.write \
    .mode("overwrite") \
    .option("batchsize", "50000") \
    .option("numPartitions", "10") \
    .jdbc(url=jdbc_url, 
          table="silver_table", 
          properties=connection_properties)

print("✅ Data successfully saved to PostgreSQL!")

# Verify the data
print("🔍 Verifying data in PostgreSQL...")
df_read = spark.read \
    .jdbc(url=jdbc_url, 
          table="silver_table", 
          properties=connection_properties)

print(f"📊 Rows in PostgreSQL: {df_read.count()}")
df_read.show(5)

spark.stop()
print("✅ Done!")