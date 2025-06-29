import sagemaker
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
from sagemaker.workflow.properties import PropertyFile
from sagemaker.model_metrics import ModelMetrics
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.parameters import ParameterString
import os

def get_abalone_pipeline(
    sagemaker_role,
    s3_bucket,
    mlflow_tracking_uri,
    db_endpoint,
    db_password,
    pipeline_name="AbaloneMLOpsPipeline",
    model_package_group_name="AbaloneModelPackageGroup",
    base_job_prefix="abalone"
):
    pipeline_session = PipelineSession()
    
    # Parameters for pipeline execution
    processing_instance_count = 1
    processing_instance_type = "ml.m5.large"
    training_instance_type = "ml.m5.large"
    model_approval_status = "PendingManualApproval"
    
    mlflow_tracking_uri_param = ParameterString(
        name="MlflowTrackingUri",
        default_value=mlflow_tracking_uri,
    )
    db_endpoint_param = ParameterString(
        name="DbEndpoint",
        default_value=db_endpoint,
    )
    db_password_param = ParameterString(
        name="DbPassword",
        default_value=db_password,
    )
    
    # ========== PROCESSING STEP ==========
    
    script_preprocessor = ScriptProcessor(
        image_uri=None, # SDK will use a default image
        command=["python3"],
        instance_type=processing_instance_type,
        instance_count=processing_instance_count,
        base_job_name=f"{base_job_prefix}/preprocess",
        sagemaker_session=pipeline_session,
        role=sagemaker_role,
        entry_point="src/preprocess.py",
        dependencies=["pipelines/requirements.txt"],
        arguments=[
            "--db_endpoint", db_endpoint_param,
            "--db_password", db_password_param,
        ]
    )
    
    step_process = ProcessingStep(
        name="PreprocessAbaloneData",
        processor=script_preprocessor,
        inputs=[],
        outputs=[
            ProcessingOutput(output_name="train", source="/opt/ml/processing/train"),
            ProcessingOutput(output_name="validation", source="/opt/ml/processing/validation"),
            ProcessingOutput(output_name="test", source="/opt/ml/processing/test"),
        ],
    )
    
    # ========== TRAINING STEP ==========

    image_uri = sagemaker.image_uris.retrieve(
        framework="xgboost",
        region=pipeline_session.boto_region_name,
        version="1.5-1",
        py_version="py3",
        instance_type=training_instance_type,
    )

    xgb_trainer = Estimator(
        image_uri=image_uri,
        instance_type=training_instance_type,
        instance_count=1,
        output_path=f"s3://{s3_bucket}/{base_job_prefix}/training/output",
        base_job_name=f"{base_job_prefix}/train",
        sagemaker_session=pipeline_session,
        role=sagemaker_role,
        entry_point="train.py",
        source_dir="src",
        dependencies=["pipelines/requirements.txt"],
        hyperparameters={
            "objective": "reg:squarederror",
            "num_round": 100,
            "max_depth": 5,
            "eta": 0.2,
            "gamma": 4,
            "min_child_weight": 6,
            "subsample": 0.8,
            "tracking_uri": mlflow_tracking_uri_param,
            "experiment_name": "abalone-age-prediction"
        },
    )

    step_train = TrainingStep(
        name="TrainAbaloneModel",
        estimator=xgb_trainer,
        inputs={
            "train": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
                content_type="text/csv",
            ),
            "validation": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs["validation"].S3Output.S3Uri,
                content_type="text/csv",
            ),
        },
    )
    
    # ========== EVALUATION STEP ==========

    script_evaluator = ScriptProcessor(
        image_uri=None, # SDK will use a default image
        command=["python3"],
        instance_type=processing_instance_type,
        instance_count=1,
        base_job_name=f"{base_job_prefix}/evaluate",
        sagemaker_session=pipeline_session,
        role=sagemaker_role,
    )

    evaluation_report = PropertyFile(
        name="AbaloneEvaluationReport",
        output_name="evaluation",
        path="evaluation.json",
    )

    step_evaluate = ProcessingStep(
        name="EvaluateAbaloneModel",
        processor=script_evaluator,
        inputs=[
            ProcessingInput(
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=step_process.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(output_name="evaluation", source="/opt/ml/processing/evaluation"),
        ],
        code="src/evaluate.py",
        property_files=[evaluation_report],
    )
    
    # ========== REGISTER MODEL STEP ==========
    
    model_metrics = ModelMetrics(
        model_statistics=sagemaker.model_metrics.MetricsSource(
            s3_uri=step_evaluate.properties.ProcessingOutputConfig.Outputs["evaluation"].S3Output.S3Uri,
            file_path="evaluation.json",
            content_type="application/json",
        )
    )

    step_register = RegisterModel(
        name="RegisterAbaloneModel",
        estimator=xgb_trainer,
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=["ml.t2.medium", "ml.m5.large"],
        transform_instances=["ml.m5.large"],
        model_package_group_name=model_package_group_name,
        approval_status=model_approval_status,
        model_metrics=model_metrics,
    )
    
    # ========== PIPELINE INSTANCE ==========
    
    pipeline = sagemaker.workflow.pipeline.Pipeline(
        name=pipeline_name,
        parameters=[
            mlflow_tracking_uri_param,
            db_endpoint_param,
            db_password_param,
            processing_instance_count,
            processing_instance_type,
            training_instance_type,
            model_approval_status,
        ],
        steps=[step_process, step_train, step_evaluate, step_register],
        sagemaker_session=pipeline_session,
    )
    
    return pipeline 