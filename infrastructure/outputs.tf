output "s3_bucket_name" {
  description = "The name of the S3 bucket created for pipeline artifacts."
  value       = data.aws_s3_bucket.existing_bucket.bucket
}

output "model_package_group_name" {
  description = "The name of the SageMaker Model Package Group."
  value       = aws_sagemaker_model_package_group.abalone_group.model_package_group_name
}

output "api_ecr_repository_url" {
  description = "The URL of the ECR repository for the API."
  value       = aws_ecr_repository.api_repository.repository_url
}

output "ui_ecr_repository_url" {
  description = "The URL of the ECR repository for the UI."
  value       = aws_ecr_repository.ui_repository.repository_url
}

output "mlflow_db_endpoint" {
  description = "The endpoint of the MLflow RDS database."
  value       = aws_db_instance.mlflow_db.endpoint
}

output "db_password" {
  description = "The auto-generated password for the RDS database."
  value       = random_password.db_password.result
  sensitive   = true
}

output "sagemaker_role_arn" {
  description = "The ARN of the IAM role for SageMaker."
  value       = aws_iam_role.sagemaker_role.arn
}

output "lambda_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  value       = aws_iam_role.lambda_role.arn
}

output "github_actions_role_arn" {
  description = "The ARN of the IAM role for GitHub Actions."
  value       = aws_iam_role.github_actions_role.arn
}

output "eks_cluster_name" {
  description = "The name of the EKS cluster."
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "The endpoint for the EKS cluster."
  value       = aws_eks_cluster.main.endpoint
}

output "sagemaker_studio_domain_id" {
  description = "The ID of the SageMaker Studio Domain."
  value       = aws_sagemaker_domain.studio_domain.id
}

output "mlflow_db_connection_string" {
  description = "Connection string for MLflow database (for manual MLflow deployment)."
  value       = "postgresql://${aws_db_instance.mlflow_db.username}:${random_password.db_password.result}@${aws_db_instance.mlflow_db.address}:5432/${aws_db_instance.mlflow_db.db_name}"
  sensitive   = true
} 