#!/bin/bash

# Deploy MLflow to EKS Cluster
echo "🚀 Deploying MLflow to EKS cluster..."

# Configure kubectl to connect to EKS cluster
echo "📡 Configuring kubectl for EKS cluster..."
aws eks update-kubeconfig --region us-east-1 --name abalone-mlops

# Add Bitnami Helm repository
echo "📦 Adding Bitnami Helm repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Get database connection details from Terraform outputs
echo "🔍 Getting database connection details..."
cd infrastructure
DB_HOST=$(terraform output -raw mlflow_db_endpoint | cut -d':' -f1)
DB_PASSWORD=$(terraform output -raw db_password)
cd ..

echo "Database Host: $DB_HOST"

# Create MLflow namespace
echo "🏗️ Creating MLflow namespace..."
kubectl create namespace mlflow --dry-run=client -o yaml | kubectl apply -f -

# Deploy MLflow with external PostgreSQL
echo "🎯 Deploying MLflow..."
helm upgrade --install mlflow bitnami/mlflow \
  --namespace mlflow \
  --set tracking.auth.enabled=false \
  --set postgresql.enabled=false \
  --set externalDatabase.host="$DB_HOST" \
  --set externalDatabase.port=5432 \
  --set externalDatabase.database="mlflowdb" \
  --set externalDatabase.user="mlflow" \
  --set externalDatabase.password="$DB_PASSWORD" \
  --set service.type=LoadBalancer \
  --set service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"="nlb" \
  --wait --timeout=10m

# Get MLflow URL
echo "🌐 Getting MLflow URL..."
echo "Waiting for LoadBalancer to be ready..."
kubectl wait --namespace mlflow --for=condition=ready pod --selector=app.kubernetes.io/name=mlflow --timeout=300s

MLFLOW_URL=$(kubectl get svc mlflow -n mlflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

if [ -z "$MLFLOW_URL" ]; then
    echo "⏳ LoadBalancer still provisioning, getting service details..."
    kubectl get svc mlflow -n mlflow
    echo ""
    echo "📋 Run this command in a few minutes to get the URL:"
    echo "kubectl get svc mlflow -n mlflow -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"
else
    echo ""
    echo "🎉 MLflow is deployed successfully!"
    echo "🌐 MLflow URL: http://$MLFLOW_URL"
    echo ""
    echo "📊 Access your MLflow UI at: http://$MLFLOW_URL"
fi

echo ""
echo "✅ MLflow deployment completed!" 