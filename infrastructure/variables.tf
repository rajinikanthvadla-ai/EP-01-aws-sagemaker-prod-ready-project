variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
}

variable "project_name" {
  description = "The name of the project, used for resource naming."
  type        = string
  default     = "abalone-mlops"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing pipeline artifacts."
  type        = string
}

variable "github_repo" {
  description = "The GitHub repository in owner/repo format."
  type        = string
}

variable "github_pat" {
  description = "A GitHub Personal Access Token with repo scope."
  type        = string
  sensitive   = true
}

variable "oidc_provider_arn" {
  description = "The ARN of the IAM OIDC provider for GitHub Actions."
  type        = string
}

variable "cluster_name" {
  description = "The name for the EKS cluster."
  type        = string
  default     = "abalone-mlops-cluster"
} 