# 🚀 PART 2: MLOps Application Deployment & Workflow Setup

Congratulations! Your infrastructure is successfully deployed. Now let's deploy the applications and set up the complete MLOps workflow.

## 📋 **What We'll Deploy in Part 2:**

1. **MLflow Tracking Server** - Experiment tracking and model registry
2. **SageMaker ML Pipeline** - Training, evaluation, and model registration
3. **FastAPI Application** - Model inference API
4. **Streamlit UI** - User interface for predictions
5. **Complete CI/CD Pipeline** - Automated deployment workflow

---

## 🎯 **Step 1: Deploy MLflow to EKS via GitHub Actions**

### **🚀 Automated Deployment (Recommended)**

1. **Go to your GitHub repository**
2. **Click on "Actions" tab**
3. **Find "Deploy MLflow to EKS" workflow**
4. **Click "Run workflow"**
5. **Ensure "Deploy MLflow to EKS cluster" is checked**
6. **Click "Run workflow" button**

### **📊 Monitor Deployment:**

The GitHub Actions workflow will:
- ✅ Configure kubectl for your EKS cluster
- ✅ Get database connection details from Terraform
- ✅ Deploy MLflow using Bitnami Helm chart
- ✅ Create LoadBalancer service
- ✅ Output the MLflow URL

### **🌐 Getting MLflow URL:**

After the workflow completes:
1. **Check the workflow logs** for the MLflow URL
2. **Look for this output:**
   ```
   🎉 MLflow deployed successfully!
   🌐 MLflow URL: http://YOUR_LOADBALANCER_URL
   ```
3. **If LoadBalancer is still provisioning**, wait 2-3 minutes and check the workflow logs again

---

## 🎯 **Step 2: Configure GitHub Secrets for Application Deployment**

Add these additional secrets to your GitHub repository:

### **Required Secrets:**
```bash
# AWS ECR and EKS Access
ECR_REGISTRY=911167906047.dkr.ecr.us-east-1.amazonaws.com
EKS_CLUSTER_NAME=abalone-mlops

# MLflow Configuration
MLFLOW_TRACKING_URI=http://YOUR_MLFLOW_URL  # From Step 1
MLFLOW_DB_HOST=terraform-20250629133025003000000001.cfi6ckwcmyhv.us-east-1.rds.amazonaws.com
MLFLOW_DB_PASSWORD=<your-db-password>  # From terraform output

# SageMaker Configuration  
SAGEMAKER_ROLE_ARN=arn:aws:iam::911167906047:role/SageMakerExecutionRole
MODEL_PACKAGE_GROUP_NAME=AbaloneModelPackageGroup
```

---

## 🎯 **Step 3: Run the SageMaker ML Pipeline via GitHub Actions**

### **🚀 Trigger the Pipeline:**

**Option 1: Manual Trigger (Recommended)**
1. **Go to your GitHub repository**
2. **Click "Actions" tab**
3. **Find "ML Pipeline - Train and Register Model" workflow**
4. **Click "Run workflow"**
5. **Optionally customize experiment name**
6. **Click "Run workflow" button**

**Option 2: Automatic Trigger**
- Pipeline automatically runs when you push changes to:
  - `src/**` (ML code)
  - `pipelines/**` (Pipeline definitions)
  - `notebooks/**` (Jupyter notebooks)

### **📊 Monitor Pipeline:**
- **GitHub Actions**: Real-time pipeline progress and logs
- **SageMaker Console**: Check pipeline execution status
- **MLflow UI**: View experiment tracking and metrics

### **🎯 Pipeline Steps:**
The workflow will automatically:
- ✅ Set up Python environment
- ✅ Install ML dependencies
- ✅ Execute SageMaker pipeline
- ✅ Train XGBoost model
- ✅ Log metrics to MLflow
- ✅ Register model (if performance criteria met)

---

## 🎯 **Step 4: Deploy Applications to EKS**

### **Applications to Deploy:**
1. **FastAPI Inference Service** - REST API for predictions
2. **Streamlit UI** - Web interface for users

### **Deployment Process:**
The applications will be automatically deployed via GitHub Actions when:
- ML pipeline completes successfully
- Model is registered in MLflow
- Docker images are built and pushed to ECR

### **Manual Deployment (if needed):**

```bash
# Deploy API
kubectl apply -f kubernetes/api-deployment.yaml

# Deploy UI  
kubectl apply -f kubernetes/ui-deployment.yaml

# Get service URLs
kubectl get svc -n default
```

---

## 🎯 **Step 5: Test the Complete Workflow**

### **1. Test MLflow:**
```bash
# Access MLflow UI
echo "MLflow URL: http://$(kubectl get svc mlflow -n mlflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')"
```

### **2. Test API:**
```bash
# Get API URL
API_URL=$(kubectl get svc abalone-api -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test prediction
curl -X POST "http://$API_URL/predict" \
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

### **3. Test UI:**
```bash
# Get UI URL
UI_URL=$(kubectl get svc abalone-ui -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "UI URL: http://$UI_URL"
```

---

## 🎯 **Step 6: Verify Complete MLOps Workflow**

### **End-to-End Flow:**
1. ✅ **Data Processing** - Preprocessing pipeline
2. ✅ **Model Training** - XGBoost training in SageMaker
3. ✅ **Model Evaluation** - Metrics logged to MLflow
4. ✅ **Model Registry** - Approved models registered
5. ✅ **Model Deployment** - API serves latest approved model
6. ✅ **Monitoring** - Predictions logged for retraining
7. ✅ **CI/CD** - Automated pipeline on code changes

### **Verification Checklist:**
- [ ] MLflow UI accessible and showing experiments
- [ ] SageMaker pipeline completed successfully
- [ ] Model registered in MLflow model registry
- [ ] FastAPI service responding to predictions
- [ ] Streamlit UI accessible and functional
- [ ] GitHub Actions pipelines running successfully

---

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. MLflow LoadBalancer not ready:**
```bash
# Check service status
kubectl get svc mlflow -n mlflow
kubectl describe svc mlflow -n mlflow

# Check pods
kubectl get pods -n mlflow
kubectl logs -n mlflow deployment/mlflow
```

**2. Application deployment fails:**
```bash
# Check GitHub Actions logs
# Verify ECR repository permissions
# Check EKS cluster connectivity
```

**3. Database connection issues:**
```bash
# Verify security group rules
# Check RDS endpoint accessibility
# Validate database credentials
```

---

## 📊 **Monitoring & Management**

### **Key URLs:**
- **MLflow UI**: `http://YOUR_MLFLOW_URL`
- **API Endpoint**: `http://YOUR_API_URL/docs`
- **Streamlit UI**: `http://YOUR_UI_URL`
- **SageMaker Console**: AWS Console → SageMaker → Pipelines

### **Useful Commands:**
```bash
# Check all services
kubectl get svc --all-namespaces

# View logs
kubectl logs -f deployment/mlflow -n mlflow
kubectl logs -f deployment/abalone-api
kubectl logs -f deployment/abalone-ui

# Scale applications
kubectl scale deployment abalone-api --replicas=3
kubectl scale deployment abalone-ui --replicas=2
```

---

## 🎉 **Success! Your MLOps Platform is Ready**

You now have a complete, production-ready MLOps platform with:
- ✅ **Infrastructure as Code** (Terraform)
- ✅ **Container Orchestration** (EKS)
- ✅ **Experiment Tracking** (MLflow)
- ✅ **ML Pipelines** (SageMaker)
- ✅ **Model Serving** (FastAPI)
- ✅ **User Interface** (Streamlit)
- ✅ **CI/CD Automation** (GitHub Actions)

**Next Steps:**
1. Run the MLflow deployment script
2. Configure the additional GitHub secrets
3. Trigger the ML pipeline
4. Access your applications via the LoadBalancer URLs

**Happy MLOps! 🚀** 