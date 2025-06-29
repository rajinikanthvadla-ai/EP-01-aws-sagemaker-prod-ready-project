# 🚀 PART 2: Complete MLOps Deployment Guide

**Prerequisites:** ✅ Infrastructure successfully deployed (PART 1 completed)

Your infrastructure outputs:
```
api_ecr_repository_url = "911167906047.dkr.ecr.us-east-1.amazonaws.com/abalone-prediction-api"
eks_cluster_name = "abalone-mlops"
github_actions_role_arn = "arn:aws:iam::911167906047:role/GitHubActionRole"
sagemaker_role_arn = "arn:aws:iam::911167906047:role/SageMakerExecutionRole"
ui_ecr_repository_url = "911167906047.dkr.ecr.us-east-1.amazonaws.com/abalone-prediction-ui"
```

---

## 📋 **What You'll Deploy:**

1. **MLflow Tracking Server** → Experiment tracking & model registry
2. **SageMaker ML Pipeline** → Train XGBoost model on Abalone dataset  
3. **FastAPI Application** → REST API for model predictions
4. **Streamlit UI** → Web interface for users
5. **Complete automation** → End-to-end MLOps workflow

---

## 🎯 **STEP 1: Deploy MLflow Tracking Server**

### **1.1 Run the MLflow Deployment Workflow**

1. **Go to your GitHub repository**
2. **Click the "Actions" tab**
3. **Find "Deploy MLflow to EKS" workflow**
4. **Click "Run workflow" button (top right)**
5. **Ensure checkbox is checked: "Deploy MLflow to EKS cluster"**
6. **Click green "Run workflow" button**

### **1.2 Monitor the Deployment (5-10 minutes)**

Watch the workflow progress:
- ✅ Configure kubectl for EKS
- ✅ Get database connection details
- ✅ Deploy MLflow using Helm
- ✅ Create LoadBalancer service

### **1.3 Get MLflow URL**

Look for this output in the workflow logs:
```
🎉 MLflow deployed successfully!
🌐 MLflow URL: http://a1234567890abcdef-1234567890.us-east-1.elb.amazonaws.com
📊 Access your MLflow UI at: http://a1234567890abcdef-1234567890.us-east-1.elb.amazonaws.com
```

**⚠️ IMPORTANT:** Copy this MLflow URL - you'll need it for the next step!

---

## 🎯 **STEP 2: Add Required GitHub Secrets**

### **2.1 Go to Repository Settings**

1. **Click "Settings" tab** in your GitHub repository
2. **Click "Secrets and variables"** in left sidebar
3. **Click "Actions"**
4. **Click "New repository secret"**

### **2.2 Add These Secrets (One by One):**

**Secret 1: AWS_ACCOUNT_ID**
- Name: `AWS_ACCOUNT_ID`
- Value: `911167906047`

**Secret 2: MLFLOW_TRACKING_URI**
- Name: `MLFLOW_TRACKING_URI`  
- Value: `http://YOUR_MLFLOW_URL_FROM_STEP_1`
- Example: `http://a1234567890abcdef-1234567890.us-east-1.elb.amazonaws.com`

**Secret 3: SAGEMAKER_ROLE_ARN**
- Name: `SAGEMAKER_ROLE_ARN`
- Value: `arn:aws:iam::911167906047:role/SageMakerExecutionRole`

**Secret 4: MODEL_PACKAGE_GROUP_NAME**
- Name: `MODEL_PACKAGE_GROUP_NAME`
- Value: `AbaloneModelPackageGroup`

### **2.3 Verify Secrets**

You should now have these secrets:
- ✅ `AWS_REGION` (from PART 1)
- ✅ `AWS_ACCOUNT_ID` (new)
- ✅ `MLFLOW_TRACKING_URI` (new)
- ✅ `SAGEMAKER_ROLE_ARN` (new)
- ✅ `MODEL_PACKAGE_GROUP_NAME` (new)
- ✅ `GITHUB_ACTIONS_ROLE_ARN` (from PART 1)
- ✅ Other secrets from PART 1

---

## 🎯 **STEP 3: Run ML Pipeline to Train Model**

### **3.1 Run the ML Pipeline Workflow**

1. **Go to "Actions" tab**
2. **Find "ML Pipeline - Train and Register Model" workflow**
3. **Click "Run workflow"**
4. **Optional: Change experiment name** (default: "abalone-age-prediction")
5. **Click green "Run workflow" button**

### **3.2 Monitor ML Pipeline (15-20 minutes)**

The workflow will:
- ✅ Set up Python environment
- ✅ Install ML dependencies  
- ✅ Execute SageMaker pipeline
- ✅ Download Abalone dataset
- ✅ Train XGBoost model
- ✅ Log metrics to MLflow
- ✅ Register model (if performance is good)

### **3.3 Check Results**

**In MLflow UI:**
1. **Open your MLflow URL** from Step 1
2. **Click "Experiments"** 
3. **You should see "abalone-age-prediction" experiment**
4. **Click on the experiment to see runs and metrics**

**Expected metrics:**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- R² Score

---

## 🎯 **STEP 4: Deploy Applications (API + UI)**

### **4.1 Run the Application Deployment Workflow**

1. **Go to "Actions" tab**
2. **Find "Deploy Applications to EKS" workflow**
3. **Click "Run workflow"**
4. **Ensure checkbox is checked: "Deploy API and UI applications"**
5. **Click green "Run workflow" button**

### **4.2 Monitor Deployment (10-15 minutes)**

The workflow will:
- ✅ Build API Docker image
- ✅ Build UI Docker image  
- ✅ Push images to ECR
- ✅ Deploy API to EKS
- ✅ Deploy UI to EKS
- ✅ Create LoadBalancer services

### **4.3 Get Application URLs**

Look for this output in the workflow logs:
```
🔗 Application URLs (may take 2-3 minutes for LoadBalancers):
🔌 API URL: http://api-loadbalancer-url.us-east-1.elb.amazonaws.com
🖥️ UI URL: http://ui-loadbalancer-url.us-east-1.elb.amazonaws.com
```

**⚠️ IMPORTANT:** Copy these URLs - these are your live applications!

---

## 🎯 **STEP 5: Test Your Complete MLOps System**

### **5.1 Test MLflow UI**
1. **Open MLflow URL** from Step 1
2. **Verify you can see experiments and models**
3. **Check that your model training run is logged**

### **5.2 Test API**

**Option A: Using curl**
```bash
curl -X POST "http://YOUR_API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "length": 0.455,
    "diameter": 0.365,
    "height": 0.095,
    "whole_weight": 0.514,
    "shucked_weight": 0.2245,
    "viscera_weight": 0.101,
    "shell_weight": 0.15,
    "sex": "M"
  }'
```

**Expected Response:**
```json
{
  "prediction": 8.5,
  "model_version": "1",
  "prediction_id": "abc123"
}
```

**Option B: API Documentation**
1. **Open** `http://YOUR_API_URL/docs`
2. **Try the /predict endpoint** with sample data

### **5.3 Test Streamlit UI**
1. **Open UI URL** from Step 4
2. **Enter abalone measurements** in the form
3. **Click "Predict Age"**
4. **Verify you get a prediction result**

---

## 🎯 **STEP 6: Verify Complete Workflow**

### **6.1 End-to-End Flow Check**

✅ **Data Pipeline**: Automatic data download and preprocessing  
✅ **Model Training**: XGBoost trained in SageMaker  
✅ **Experiment Tracking**: Metrics logged in MLflow  
✅ **Model Registry**: Model registered and versioned  
✅ **API Deployment**: REST API serving predictions  
✅ **UI Deployment**: Web interface for users  
✅ **Infrastructure**: Everything running on AWS EKS  

### **6.2 Key URLs Summary**

**Copy these for your records:**
```
MLflow UI:     http://YOUR_MLFLOW_URL
API Endpoint:  http://YOUR_API_URL
API Docs:      http://YOUR_API_URL/docs  
Streamlit UI:  http://YOUR_UI_URL
```

---

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. MLflow URL not working**
- Wait 2-3 minutes for LoadBalancer
- Check workflow logs for errors
- Verify EKS cluster is running

**2. Application URLs showing "Pending"**
- LoadBalancers take 2-3 minutes to provision
- Check deployment status in workflow logs

**3. API returning errors**
- Check if model was registered in MLflow
- Verify API logs: workflow will show pod status

**4. Secrets not working**
- Double-check secret names (case-sensitive)
- Ensure MLflow URL includes `http://`

### **Useful Commands (if needed):**
```bash
# Check all services
kubectl get svc --all-namespaces

# Check pod status  
kubectl get pods

# Get service URLs
kubectl get svc abalone-api
kubectl get svc abalone-ui
kubectl get svc mlflow -n mlflow
```

---

## 🎉 **SUCCESS! Your MLOps Platform is Live**

You now have a complete, production-ready MLOps platform:

### **🏗️ Infrastructure:**
- ✅ EKS Kubernetes cluster
- ✅ RDS PostgreSQL database
- ✅ ECR container repositories
- ✅ IAM roles and permissions

### **🤖 ML Platform:**
- ✅ MLflow for experiment tracking
- ✅ SageMaker for ML pipelines
- ✅ XGBoost model trained and registered
- ✅ Automated model versioning

### **🚀 Applications:**
- ✅ FastAPI for model inference
- ✅ Streamlit UI for user interaction
- ✅ LoadBalancer services for external access
- ✅ Container orchestration with Kubernetes

### **⚙️ Automation:**
- ✅ GitHub Actions CI/CD pipelines
- ✅ Automated model training
- ✅ Automated application deployment
- ✅ Infrastructure as Code

### **📊 Monitoring:**
- ✅ Experiment tracking in MLflow
- ✅ Model performance metrics
- ✅ Application logs in Kubernetes
- ✅ AWS CloudWatch integration

---

## 🎯 **What's Next?**

Your MLOps platform is ready for:
1. **Adding new models** - Modify pipeline for different datasets
2. **Scaling applications** - Increase replicas in Kubernetes
3. **Adding monitoring** - Set up alerts and dashboards
4. **Implementing A/B testing** - Deploy multiple model versions
5. **Adding data pipelines** - Connect to real data sources

**Congratulations! You've built a complete, enterprise-grade MLOps platform! 🚀** 