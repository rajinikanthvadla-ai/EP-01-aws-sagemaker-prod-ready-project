# Guide: Part 1 - Provisioning Your MLOps Platform

Follow these instructions precisely. At the end, your entire MLOps platform infrastructure will be live on AWS, ready for the application and ML pipelines.

---

### **Step 1: Prerequisites (Your Local Machine)**

Before you begin, ensure you have the following:

1.  **An AWS Account:** You need an account with administrator-level permissions to create the necessary resources (IAM roles, EKS, RDS, etc.).
2.  **A GitHub Account:** All code and pipelines are managed through your GitHub repository.
3.  **A GitHub Personal Access Token (PAT):**
    *   Go to your GitHub **Settings -> Developer settings -> Personal access tokens -> Tokens (classic)**.
    *   Click **Generate new token**.
    *   Give it a note (e.g., "MLOps Project").
    *   Select the **`repo`** scope. This is required for the Lambda function to trigger workflows.
    *   Click **Generate token** and **copy it immediately**. You will not see it again.

---

### **Step 2: Bootstrap Trust in AWS (One-Time Manual Setup)**

This is the **only manual step** you need to perform in the AWS console. It tells your AWS account to trust your GitHub repository to request temporary credentials.

1.  Sign in to your AWS Management Console.
2.  Navigate to the **IAM** service.
3.  On the left menu, click **Identity providers**.
4.  Click the **Add provider** button.
5.  For the provider type, select **OpenID Connect**.
6.  In the **Provider URL** field, enter exactly: `https://token.actions.githubusercontent.com`
7.  For the **Audience** field, enter exactly: `sts.amazonaws.com`
8.  Click the **Get thumbprint** button to verify the provider.
9.  Click the **Add provider** button at the bottom.
10. After the provider is created, click on its name in the list and **copy the full ARN**. It will look like `arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com`.

---

### **Step 3: Configure Your Infrastructure Secrets in GitHub**

The infrastructure pipeline needs these secrets to authenticate with AWS and provision the resources.

1.  In your GitHub repository, navigate to **Settings > Secrets and variables > Actions**.
2.  Click the **New repository secret** button for each of the following secrets:
    *   `AWS_ACCOUNT_ID`: Your 12-digit AWS Account ID.
    *   `AWS_REGION`: The AWS region you want to build in (e.g., `us-east-1`).
    *   `S3_BUCKET_NAME`: A **globally unique name** for the S3 bucket that will be created (e.g., `your-initials-abalone-mlops-artifacts`).
    *   `GH_REPO`: Your repository name in the exact `owner/repository_name` format (e.g., `john-doe/mlops-project`).
    *   `OIDC_PROVIDER_ARN`: The full ARN you copied in **Step 2**.
    *   `GH_PAT`: The Personal Access Token you created in **Step 1**.

---

### **Step 4: Execute the "One-Click" Infrastructure Pipeline**

This step will build everything.

1.  In your GitHub repository, click on the **Actions** tab.
2.  On the left sidebar, you will see the **"Terraform - Provision Infrastructure"** workflow. Click on it.
3.  You will see a message: "This workflow has a `workflow_dispatch` event trigger." Click the **Run workflow** dropdown button on the right side of the screen.
4.  Leave the branch set to `main` and click the green **Run workflow** button.
5.  **Be patient.** This workflow will take **15-20 minutes** to complete because it is provisioning an entire Kubernetes cluster, a VPC, and a database from scratch. You can click on the `terraform` job to watch the live logs.

---

### **Step 5: Harvest Your Platform's Endpoints and Credentials**

Once the workflow from Step 4 completes successfully, you need to gather the outputs.

1.  Click on the completed "Terraform - Provision Infrastructure" workflow run.
2.  Click on the `terraform` job in the summary.
3.  Scroll through the logs to the very end. You will see a section with the **Terraform Outputs**. It will look something like this:
    ```
    Outputs:

    api_ecr_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/abalone-prediction-api"
    db_password = <sensitive>
    eks_cluster_name = "abalone-mlops-cluster"
    github_actions_role_arn = "arn:aws:iam::123456789012:role/GitHubActionRole"
    mlflow_db_endpoint = "mlflowdb.cxyz....us-east-1.rds.amazonaws.com"
    mlflow_url = "a123....elb.us-east-1.amazonaws.com"
    ...and so on
    ```
4.  Copy these output values into a temporary text file. To see the `db_password`, you may need to expand the `Terraform Apply` step in the log.

---

### **Step 6: Configure the Application Pipelines**

Now, provide the live infrastructure details to your application pipelines by creating a final set of secrets.

1.  Go back to your repository's **Settings > Secrets and variables > Actions**.
2.  Add the following **new** repository secrets, using the values you copied in **Step 5**:
    *   `DB_ENDPOINT`: The `mlflow_db_endpoint` value.
    *   `DB_PASSWORD`: The `db_password` sensitive value.
    *   `SAGEMAKER_ROLE_ARN`: The `sagemaker_role_arn` value.
    *   `EKS_CLUSTER_NAME`: The `eks_cluster_name` value.
    *   `MLFLOW_TRACKING_URI`: The public `mlflow_url` value. Ensure you include `http://` at the beginning.

---

**Part 1 is now complete.** You have successfully provisioned a production-grade MLOps platform with a single click. The MLflow server is live, the EKS cluster is running, and all the triggers and permissions are in place. The system is now ready for you to run the ML and application deployment pipelines. 