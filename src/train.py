import argparse
import os
import pandas as pd
import xgboost as xgb
import joblib
import mlflow
import mlflow.xgboost

def main():
    parser = argparse.ArgumentParser()

    # Hyperparameters are passed as command-line arguments.
    parser.add_argument("--max_depth", type=int, default=5)
    parser.add_argument("--eta", type=float, default=0.2)
    parser.add_argument("--gamma", type=int, default=4)
    parser.add_argument("--min_child_weight", type=int, default=6)
    parser.add_argument("--subsample", type=float, default=0.8)
    parser.add_argument("--objective", type=str, default="reg:squarederror")
    parser.add_argument("--num_round", type=int, default=100)

    # MLflow arguments
    parser.add_argument("--tracking_uri", type=str, required=True)
    parser.add_argument("--experiment_name", type=str, required=True)

    # SageMaker specific arguments. Defaults are provided.
    parser.add_argument("--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR"))
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--validation", type=str, default=os.environ.get("SM_CHANNEL_VALIDATION"))

    args, _ = parser.parse_known_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment_name)

    with mlflow.start_run():
        # Load data
        train_data = pd.read_csv(os.path.join(args.train, "train.csv"), header=None)
        val_data = pd.read_csv(os.path.join(args.validation, "validation.csv"), header=None)

        # Separate labels and features
        X_train, y_train = train_data.iloc[:, 1:], train_data.iloc[:, 0]
        X_val, y_val = val_data.iloc[:, 1:], val_data.iloc[:, 0]

        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # Log hyperparameters
        params = {
            "max_depth": args.max_depth,
            "eta": args.eta,
            "gamma": args.gamma,
            "min_child_weight": args.min_child_weight,
            "subsample": args.subsample,
            "objective": args.objective,
        }
        mlflow.log_params(params)
        
        # Train the model and log metrics
        evals_result = {}
        bst = xgb.train(
            params=params,
            dtrain=dtrain,
            evals=[(dval, "validation")],
            num_boost_round=args.num_round,
            early_stopping_rounds=10,
            evals_result=evals_result
        )

        val_rmse = evals_result['validation']['rmse'][-1]
        mlflow.log_metric("validation_rmse", val_rmse)

        # Log the model using MLflow's XGBoost integration
        mlflow.xgboost.log_model(
            xgb_model=bst,
            artifact_path="model",
            registered_model_name="abalone-xgboost-model"
        )
        
        # Also save the model in the format SageMaker expects
        model_path = os.path.join(args.model_dir, "xgboost-model")
        joblib.dump(bst, model_path)
        print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main() 