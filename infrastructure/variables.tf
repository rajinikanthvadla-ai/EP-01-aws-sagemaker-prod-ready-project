variable "aws_region" {
  description = "The AWS region to create resources in."
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

variable "cluster_name" {
  description = "The name for the EKS cluster."
  type        = string
  default     = "abalone-mlops-cluster"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing pipeline artifacts."
  type        = string
} 