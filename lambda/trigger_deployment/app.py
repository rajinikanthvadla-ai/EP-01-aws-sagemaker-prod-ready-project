import json
import boto3
import os
import requests

# Environment variables
GITHUB_TOKEN_SECRET_NAME = os.environ.get("GITHUB_TOKEN_SECRET_NAME", "github-pat-for-mlops")
GITHUB_REPO = os.environ.get("GITHUB_REPO") # e.g., "my-org/my-repo"
REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")

def get_github_token():
    """Retrieves the GitHub PAT from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=REGION_NAME)
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=GITHUB_TOKEN_SECRET_NAME
        )
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)['GITHUB_TOKEN']
        else:
            # Handle binary secret
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret.decode('utf-8')


def lambda_handler(event, context):
    """
    Lambda function triggered by EventBridge when a SageMaker Model Package state changes.
    This function triggers a GitHub Actions workflow using repository_dispatch.
    """
    print("Received event: ", json.dumps(event))

    model_package_arn = event['detail']['ModelPackageArn']
    approval_status = event['detail']['ModelApprovalStatus']

    if approval_status != "Approved":
        print(f"Model package {model_package_arn} was not approved. Status is {approval_status}. Exiting.")
        return {
            'statusCode': 200,
            'body': json.dumps('Model not approved. No action taken.')
        }

    print(f"Model {model_package_arn} was approved. Triggering deployment workflow.")

    if not GITHUB_REPO:
        raise ValueError("GITHUB_REPO environment variable is not set.")

    github_token = get_github_token()
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    
    payload = {
        "event_type": "model-approved",
        "client_payload": {
            "model_package_arn": model_package_arn
        }
    }
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print("Successfully triggered GitHub Actions workflow.")
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully triggered deployment workflow!')
        }
    except requests.exceptions.RequestException as e:
        print(f"Error triggering GitHub Actions workflow: {e}")
        raise e 