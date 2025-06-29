# Guide: Part 1 - Provisioning Your MLOps Platform

Follow these instructions precisely. At the end, your entire MLOps platform infrastructure will be live on AWS, ready for the application and ML pipelines.

---

### **Step 1: Create a "Terraform" IAM User for Bootstrapping**

For the very first run, we need a user with permissions to create the infrastructure, including the more secure OIDC roles that our other pipelines will use.

1.  Navigate to the **IAM** service in your AWS Console.
2.  Go to **Users** on the left menu and click **Create user**.
3.  Give the user a name, like `github-terraform-user`.
4.  On the next screen, select **Attach policies directly** and attach the `AdministratorAccess` policy.
    *(Note: For a real production system, you would create a more restrictive policy. For this lab, admin access is the simplest.)*
5.  Complete the user creation process.
6.  Click on the newly created user's name and go to the **Security credentials** tab.
7.  Scroll down to **Access keys** and click **Create access key**.
8.  Select **Command Line Interface (CLI)** as the use case, acknowledge the recommendation, and click **Next**.
9.  Click **Create access key** and **copy the `Access key ID` and the `Secret access key` immediately.** You will not see the secret key again.

---

### **Step 2: Manually Create an S3 Bucket for Terraform State**

Terraform needs a place to store its state file, which keeps track of the infrastructure it manages. You must create this bucket manually one time.

1.  Navigate to the **S3** service in your AWS Console.
2.  Click **Create bucket**.
3.  Give the bucket a **globally unique name** (e.g., `your-initials-abalone-terraform-state`).
4.  Leave all other settings as default and click **Create bucket**.
5.  **Remember this bucket name.**

---

### **Step 3: Configure Your Infrastructure Secrets in GitHub**

The infrastructure pipeline needs these secrets to authenticate and run.

1.  In your GitHub repository, navigate to **Settings > Secrets and variables > Actions**.
2.  Click the **New repository secret** button for each of the following secrets:
    *   `AWS_REGION`: The AWS region you want to build in (e.g., `us-east-1`).
    *   `TERRAFORM_AWS_ACCESS_KEY_ID`: The Access Key ID you copied in **Step 1**.
    *   `TERRAFORM_AWS_SECRET_ACCESS_KEY`: The Secret Access Key you copied in **Step 1**.
    *   `S3_BUCKET_NAME`: The exact name of the S3 bucket you created in **Step 2**.
    *   `GH_REPO`: Your repository name in the exact `owner/repository_name` format (e.g., `john-doe/mlops-project`).
    *   `GH_PAT`: The Personal Access Token you created in the prerequisites.
    *   `OIDC_PROVIDER_ARN`: The full ARN of the OIDC provider you created in **Step 2** of the previous version of this guide (the one starting with `arn:aws:iam...`). This is required by Terraform to build roles for the *other* pipelines.

---

### **Step 4: Execute the "One-Click" Infrastructure Pipeline**

This step will build everything.

1.  In your GitHub repository, click on the **Actions** tab.
2.  On the left sidebar, you will see the **"Terraform - Provision or Update Infrastructure"** workflow. Click on it.
3.  Click the **Run workflow** dropdown button on the right side of the screen.
4.  Leave the branch set to `main` and click the green **Run workflow** button.
5.  **Be patient.** This will still take **15-20 minutes** to provision the EKS cluster and other resources.

---

### **Step 5: Harvest and Configure Application Secrets**

Once the workflow from Step 4 completes, you need to gather the outputs and configure the secrets for the *next* set of pipelines (Build, Deploy, etc.).

1.  Click on the completed workflow run and then on the `terraform` job.
2.  Scroll to the end of the logs to find the **Terraform Outputs**. Copy the values for `mlflow_db_endpoint`, `db_password`, `sagemaker_role_arn`, etc.
3.  Go back to your repository's **Settings > Secrets and variables > Actions**.
4.  Add the following **new** repository secrets:
    *   `DB_ENDPOINT`: The `mlflow_db_endpoint` value.
    *   `DB_PASSWORD`: The `db_password` sensitive value.
    *   `SAGEMAKER_ROLE_ARN`: The `sagemaker_role_arn` value.
    *   `EKS_CLUSTER_NAME`: The `eks_cluster_name` value.
    *   `MLFLOW_TRACKING_URI`: The public `mlflow_url` value (e.g., `http://your-mlflow-url.com`).
    *   `AWS_ACCOUNT_ID`: Your 12-digit AWS Account ID.

---

### **How to Destroy Your Infrastructure**

When you are finished with the lab and want to avoid AWS costs, you can cleanly destroy all the created resources.

1.  Go to the **Actions** tab in your GitHub repository.
2.  Find and click on the **"Terraform - Destroy Infrastructure"** workflow.
3.  Click **Run workflow** to execute the job. It will use the same credentials to tear everything down.

---

**Part 1 is now complete.** You have successfully provisioned the platform. The system is now ready for Part 2: running the ML and application deployment pipelines. 