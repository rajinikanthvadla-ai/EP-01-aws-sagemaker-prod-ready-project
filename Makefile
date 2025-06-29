.PHONY: help install-deps tf-init tf-plan tf-apply tf-destroy

help:
	@echo "Commands:"
	@echo "  install-deps      : Install Python dependencies for all services."
	@echo "  tf-init           : Initialize Terraform in the infrastructure directory."
	@echo "  tf-plan           : Create a Terraform execution plan."
	@echo "  tf-apply          : Apply the Terraform plan to create infrastructure."
	@echo "  tf-destroy        : Destroy the Terraform-managed infrastructure."
	@echo "  docker-build-api  : Build the Docker image for the inference API."

install-deps:
	@echo "Installing dependencies for API..."
	python -m pip install -r api/requirements.txt
	@echo "Installing dependencies for SageMaker pipeline scripts..."
	python -m pip install sagemaker boto3

# --- Terraform Commands ---
tf-init:
	@echo "Initializing Terraform..."
	cd infrastructure && terraform init

tf-plan:
	@echo "Creating Terraform plan..."
	cd infrastructure && terraform plan

tf-apply:
	@echo "Applying Terraform plan..."
	cd infrastructure && terraform apply -auto-approve

tf-destroy:
	@echo "Destroying Terraform-managed infrastructure..."
	cd infrastructure && terraform destroy -auto-approve

# --- Docker Commands ---
docker-build-api:
	@echo "Building API Docker image..."
	docker build -t abalone-prediction-api:latest ./api 