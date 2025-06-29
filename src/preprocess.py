import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
from sklearn.preprocessing import OneHotEncoder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-test-split-ratio", type=float, default=0.3)
    parser.add_argument("--db_endpoint", type=str, required=True)
    parser.add_argument("--db_password", type=str, required=True)
    args, _ = parser.parse_known_args()

    print("Connecting to the database to fetch prediction logs.")
    database_url = f"postgresql+psycopg2://mlflow:{args.db_password}@{args.db_endpoint}/mlflowdb"
    engine = create_engine(database_url)
    
    # In a real-world scenario, you might have more complex logic to select recent data,
    # handle data drift, or sample the data. Here, we'll use all logged predictions.
    try:
        df = pd.read_sql_table("prediction_logs", engine)
        print(f"Successfully loaded {len(df)} records from the prediction_logs table.")
        # Drop columns not needed for training
        df = df.drop(columns=['id', 'timestamp', 'predicted_age'])
    except Exception as e:
        print(f"Could not read from prediction_logs table: {e}")
        print("Falling back to initial dataset for bootstrapping.")
        # Fallback to the original dataset if the log table is empty or doesn't exist yet
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/abalone/abalone.data"
        col_names = ["Sex", "Length", "Diameter", "Height", "Whole weight", 
                     "Shucked weight", "Viscera weight", "Shell weight", "Rings"]
        df = pd.read_csv(url, names=col_names)

    # One-hot encode the 'Sex' feature
    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    sex_encoded = ohe.fit_transform(df[["Sex"]])
    sex_df = pd.DataFrame(sex_encoded, columns=ohe.get_feature_names_out(["Sex"]))
    
    df = pd.concat([df.drop("Sex", axis=1), sex_df], axis=1)

    # Move target column 'Rings' to the first position, as is standard for SageMaker
    rings_col = df.pop("Rings")
    df.insert(0, "Rings", rings_col)
    
    print("Splitting data into train, validation, and test sets.")
    # Splitting data
    train_val, test = train_test_split(df, test_size=args.train_test_split_ratio, random_state=42)
    train, val = train_test_split(train_val, test_size=0.2, random_state=42)

    print(f"Train shape: {train.shape}")
    print(f"Validation shape: {val.shape}")
    print(f"Test shape: {test.shape}")

    # Saving data to the paths provided by SageMaker Processing Job
    train_output_path = "/opt/ml/processing/train"
    val_output_path = "/opt/ml/processing/validation"
    test_output_path = "/opt/ml/processing/test"
    
    os.makedirs(train_output_path, exist_ok=True)
    os.makedirs(val_output_path, exist_ok=True)
    os.makedirs(test_output_path, exist_ok=True)

    print(f"Saving train data to {train_output_path}")
    train.to_csv(os.path.join(train_output_path, "train.csv"), header=False, index=False)
    
    print(f"Saving validation data to {val_output_path}")
    val.to_csv(os.path.join(val_output_path, "validation.csv"), header=False, index=False)
    
    print(f"Saving test data to {test_output_path}")
    test.to_csv(os.path.join(test_output_path, "test.csv"), header=False, index=False)

if __name__ == "__main__":
    main() 