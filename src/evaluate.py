import os
import json
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb

def main():
    model_path = "/opt/ml/processing/model/xgboost-model"
    test_path = "/opt/ml/processing/test/test.csv"
    output_dir = "/opt/ml/processing/evaluation"
    
    # Load the model
    bst = joblib.load(model_path)
    
    # Load the test data
    test_df = pd.read_csv(test_path, header=None)
    X_test = test_df.iloc[:, 1:]
    y_test = test_df.iloc[:, 0]
    
    dtest = xgb.DMatrix(X_test)
    
    # Make predictions
    predictions = bst.predict(dtest)
    
    # Calculate RMSE
    rmse = np.sqrt(np.mean((y_test - predictions) ** 2))
    print(f"Test RMSE: {rmse}")
    
    # Save evaluation report
    report_dict = {
        "regression_metrics": {
            "rmse": {
                "value": rmse,
                "standard_deviation": "NaN"
            },
        },
    }

    os.makedirs(output_dir, exist_ok=True)
    evaluation_path = os.path.join(output_dir, "evaluation.json")
    with open(evaluation_path, "w") as f:
        f.write(json.dumps(report_dict))

if __name__ == "__main__":
    main() 