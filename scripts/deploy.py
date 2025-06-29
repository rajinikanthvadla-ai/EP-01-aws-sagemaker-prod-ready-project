import argparse
import boto3
import time
import os

def deploy_staging(model_package_arn, sagemaker_role_arn, region):
    sagemaker_client = boto3.client("sagemaker", region_name=region)
    
    model_name = f"abalone-staging-model-{int(time.time())}"
    endpoint_config_name = f"abalone-staging-endpoint-config-{int(time.time())}"
    endpoint_name = "abalone-staging"

    print(f"Creating model: {model_name}")
    sagemaker_client.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'ModelPackageName': model_package_arn
        },
        ExecutionRoleArn=sagemaker_role_arn
    )

    print(f"Creating endpoint configuration: {endpoint_config_name}")
    sagemaker_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.m5.large',
                'InitialVariantWeight': 1.0
            }
        ]
    )

    print(f"Creating/Updating endpoint: {endpoint_name}")
    try:
        sagemaker_client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
    except sagemaker_client.exceptions.ResourceNotFoundException:
        sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
    
    print("Staging deployment initiated. It may take a few minutes for the endpoint to be in service.")


def deploy_production(model_package_arn, region):
    cf_client = boto3.client("cloudformation", region_name=region)
    stack_name = "AbaloneProductionEndpoint"

    with open("scripts/cfn/production-endpoint.yml", "r") as f:
        template_body = f.read()

    print(f"Creating/Updating CloudFormation stack: {stack_name}")
    
    try:
        cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'ModelPackageArn',
                    'ParameterValue': model_package_arn
                },
            ],
            Capabilities=['CAPABILITY_IAM']
        )
        waiter = cf_client.get_waiter('stack_update_complete')
        waiter.wait(StackName=stack_name)
    except cf_client.exceptions.ClientError as e:
        if "No updates are to be performed" in str(e):
             print("No updates to be performed on the stack.")
        elif "does not exist" in str(e):
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'ModelPackageArn',
                        'ParameterValue': model_package_arn
                    },
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            waiter.wait(StackName=stack_name)
        else:
            raise e
            
    print("Production deployment via CloudFormation completed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-package-arn", type=str, required=True)
    parser.add_argument("--environment", type=str, required=True, choices=["staging", "production"])
    args = parser.parse_args()

    region = os.environ.get("AWS_REGION", "us-east-1")

    if args.environment == "staging":
        role = os.environ["SAGEMAKER_ROLE_ARN"]
        deploy_staging(args.model_package_arn, role, region)
    elif args.environment == "production":
        deploy_production(args.model_package_arn, region)

if __name__ == "__main__":
    main() 