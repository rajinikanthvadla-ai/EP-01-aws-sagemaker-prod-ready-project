# The One-Click MLOps Platform on AWS

This repository provides a complete, production-grade MLOps platform that is provisioned automatically with a **single click** from a GitHub Actions workflow. It builds the entire required infrastructure on AWS, including a Kubernetes cluster (EKS) for applications, a SageMaker Studio for ML development, and a live, internet-facing MLflow server for experiment tracking.

This is a blueprint for a fully automated, real-world ML system.

## Architecture: A Fully-Provisioned, Interconnected System

When you run the "one-click" infrastructure pipeline, it uses Terraform to build and connect all of the following components:

*   **Pillar 1: Compute & Networking (VPC & EKS)**
    *   A best-practice **Virtual Private Cloud (VPC)** to securely house all resources.
    *   A managed **Kubernetes Cluster (EKS)** to serve as the runtime platform for our live applications.

*   **Pillar 2: The ML Environment (SageMaker, MLflow, & RDS)**
    *   An **MLflow Server**, automatically deployed to EKS using a Helm chart and accessible via a public URL.
    *   A managed **PostgreSQL RDS Database**, which serves as the backend for the MLflow server and as the logging destination for our live prediction API.
    *   A **SageMaker Studio Domain**, providing a web-based IDE for data scientists, pre-configured to use the platform's roles and network.
    *   An **S3 Bucket** for the MLflow artifact store.
    *   A **SageMaker Model Package Group** for versioning our registered models.

*   **Pillar 3: Automation & CI/CD (Lambda, EventBridge, & IAM)**
    *   A **Lambda Function**, packaged and deployed automatically, which is responsible for triggering our CD pipeline.
    *   An **EventBridge Rule**, which watches for SageMaker model approvals and triggers the Lambda function.
    *   An **AWS Secrets Manager** secret to securely hold the GitHub PAT.
    *   All necessary **IAM Roles** for SageMaker, Lambda, and GitHub Actions (using OIDC for secure, passwordless authentication).

---

## How to Run This Platform: The True One-Click Guide

### Step 1: Bootstrap Trust (One-Time AWS Setup)

This one-time setup tells your AWS account to trust your GitHub repository.

1.  Navigate to **IAM -> Identity providers** in your AWS Console.
2.  Click **Add provider**, select **OpenID Connect**.
3.  Use `https://token.actions.githubusercontent.com` for the URL and `sts.amazonaws.com` for the Audience.
4.  Click **Get thumbprint** and then **Add provider**.
5.  Click on the newly created provider and **copy its ARN**.

### Step 2: Configure GitHub Secrets

This is the only manual configuration you need to do. In your GitHub repo, go to **Settings -> Secrets and variables -> Actions**. Add the following secrets:

*   `AWS_ACCOUNT_ID`: Your 12-digit AWS account ID.
*   `AWS_REGION`: The AWS region you want to deploy to (e.g., `us-east-1`).
*   `S3_BUCKET_NAME`: A **globally unique name** for the S3 bucket (e.g., `yourname-abalone-mlops-artifacts`).
*   `GH_REPO`: Your repository name in `owner/repo` format.
*   `OIDC_PROVIDER_ARN`: The ARN of the OIDC provider you created in Step 1.
*   `GH_PAT`: A GitHub Personal Access Token with `repo` scope. Terraform will use this to create the secret for the Lambda function.

### Step 3: Run the One-Click Infrastructure Pipeline

1.  Go to the **Actions** tab in your GitHub repository.
2.  Find the workflow named **"Terraform - Provision Infrastructure"** and click on it.
3.  Click **Run workflow** and then the green **Run workflow** button.
4.  **Wait for it to complete.** This will take **15-20 minutes** as it provisions the VPC and the entire EKS cluster.
5.  When it finishes, go to the `terraform` job summary page. In the logs, find the **Terraform Outputs**. You will see the live, public URL for your **MLflow dashboard**, the database credentials, and all the resource ARNs.

**Your entire platform is now live.** The MLflow UI is accessible, the Lambda trigger is active, and the EKS cluster is waiting for deployments.

### Step 4: Configure Application Pipelines with the New Infrastructure

The infrastructure pipeline created outputs that the application pipelines need. Add these as **new GitHub secrets**:

*   `DB_ENDPOINT`: The `mlflow_db_endpoint` value from the Terraform output.
*   `DB_PASSWORD`: The `db_password` value from the output.
*   `SAGEMAKER_ROLE_ARN`: The `sagemaker_role_arn` from the output.
*   `EKS_CLUSTER_NAME`: The `eks_cluster_name` from the output.
*   `MLFLOW_TRACKING_URI`: The public `mlflow_url` from the output.

### Step 5: Run the MLOps Cycle

1.  **Commit and Push:** Make a small change to any file to trigger the `build.yml` workflow.
2.  **Watch the Build:** Go to your live MLflow URL. You will see a new experiment run appear in real-time as the SageMaker pipeline executes.
3.  **Approve the Model:** In the AWS SageMaker console, under the `AbaloneModelPackageGroup`, approve the new model version.
4.  **Watch the Deployment:** This triggers the `deploy.yml` pipeline. Watch it deploy the SageMaker endpoints and then automatically deploy the API and UI applications to your EKS cluster.
5.  **Access the UI:** Find the external IP of the `abalone-ui-service` via `kubectl get svc -n default` and open it in your browser. You can now use the UI to make live predictions, which will be logged to your RDS database and can be used for the next retraining run.