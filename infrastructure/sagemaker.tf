resource "aws_sagemaker_domain" "studio_domain" {
  domain_name = "abalone-mlops-studio"
  auth_mode   = "IAM"
  
  default_user_settings {
    execution_role = aws_iam_role.sagemaker_role.arn
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
}

resource "aws_sagemaker_model_package_group" "abalone_group" {
  model_package_group_name        = "AbaloneModelPackageGroup"
  model_package_group_description = "Model package group for the abalone age prediction model."
} 