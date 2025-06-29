import os
from pipeline import get_abalone_pipeline

def main():
    
    role = os.environ["SAGEMAKER_ROLE_ARN"]
    s3_bucket = os.environ["S3_BUCKET"]
    db_endpoint = os.environ["DB_ENDPOINT"]
    db_password = os.environ["DB_PASSWORD"]

    mlflow_tracking_uri = f"postgresql+psycopg2://mlflow:{db_password}@{db_endpoint}/mlflowdb"
    
    pipeline = get_abalone_pipeline(
        sagemaker_role=role, 
        s3_bucket=s3_bucket,
        mlflow_tracking_uri=mlflow_tracking_uri
    )
    
    print("Upserting pipeline definition...")
    pipeline.upsert(role_arn=role)
    
    print("Starting pipeline execution...")
    execution = pipeline.start()
    
    print(f"Pipeline execution started with ARN: {execution.arn}")
    execution.wait()


if __name__ == "__main__":
    main() 