import boto3
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# --- Database Setup ---
DB_ENDPOINT = os.environ.get("DB_ENDPOINT")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DATABASE_URL = f"postgresql+psycopg2://mlflow:{DB_PASSWORD}@{DB_ENDPOINT}/mlflowdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the table for logging predictions
class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    sex = Column(String)
    length = Column(Float)
    diameter = Column(Float)
    height = Column(Float)
    whole_weight = Column(Float)
    shucked_weight = Column(Float)
    viscera_weight = Column(Float)
    shell_weight = Column(Float)
    predicted_age = Column(Float)

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)
# --- End Database Setup ---

app = FastAPI()

# SageMaker settings
SAGEMAKER_ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", "abalone-production")
AWS_REGION = os.environ.get("AWS_REGION", "<<AWS_REGION>>")

# Initialize boto3 client
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)

class AbaloneFeatures(BaseModel):
    # The model was trained on one-hot encoded 'Sex' feature.
    # We expect the raw 'Sex' feature here and will encode it.
    sex: str # M, F, or I
    length: float
    diameter: float
    height: float
    whole_weight: float
    shucked_weight: float
    viscera_weight: float
    shell_weight: float

@app.get("/")
def read_root():
    return {"message": "Abalone age prediction API"}

@app.post("/predict")
async def predict(features: AbaloneFeatures):
    # One-hot encode the 'Sex' feature
    # This must match the encoding used during training in preprocess.py
    sex_map = {'F': [1.0, 0.0, 0.0], 'I': [0.0, 1.0, 0.0], 'M': [0.0, 0.0, 1.0]}
    sex_encoded = sex_map.get(features.sex.upper())
    
    if sex_encoded is None:
        return {"error": "Invalid value for 'sex'. Must be 'M', 'F', or 'I'."}, 400

    # The order must match the training data columns (after 'Rings' which is the target)
    # Original columns: Length, Diameter, Height, Whole weight, Shucked weight, Viscera weight, Shell weight
    # One-hot columns (from sklearn): Sex_F, Sex_I, Sex_M
    # The order of one-hot features depends on `ohe.categories_`. Assuming ['F', 'I', 'M'].
    feature_vector = [
        features.length,
        features.diameter,
        features.height,
        features.whole_weight,
        features.shucked_weight,
        features.viscera_weight,
        features.shell_weight,
    ] + sex_encoded
    
    # Convert to CSV string for the SageMaker endpoint
    payload = ",".join(map(str, feature_vector))
    
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT_NAME,
            ContentType="text/csv",
            Body=payload
        )
        
        result = response['Body'].read().decode()
        # The result is a single value, the predicted number of rings (age)
        predicted_age = float(result)
        
        # Log prediction to the database
        db = SessionLocal()
        log_entry = PredictionLog(
            sex=features.sex,
            length=features.length,
            diameter=features.diameter,
            height=features.height,
            whole_weight=features.whole_weight,
            shucked_weight=features.shucked_weight,
            viscera_weight=features.viscera_weight,
            shell_weight=features.shell_weight,
            predicted_age=predicted_age
        )
        db.add(log_entry)
        db.commit()
        db.close()
        
        return {"predicted_age": round(predicted_age, 2)}

    except Exception as e:
        # Consider more specific error handling in production
        return {"error": str(e)}, 500

# To run this app:
# uvicorn main:app --host 0.0.0.0 --port 8080 