data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../lambda/trigger_deployment/"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "trigger_deployment" {
  function_name    = "TriggerMLOpsDeployment"
  handler          = "app.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      GITHUB_REPO              = var.github_repo
      GITHUB_TOKEN_SECRET_NAME = aws_secretsmanager_secret.github_pat.name
    }
  }

  timeout = 30
}

resource "aws_cloudwatch_event_rule" "sagemaker_approval_rule" {
  name        = "SageMakerModelApprovalRule"
  description = "Fires when a SageMaker Model Package approval state changes"

  event_pattern = jsonencode({
    "source": ["aws.sagemaker"],
    "detail-type": ["SageMaker Model Package State Change"],
    "detail": {
      "ModelApprovalStatus": ["Approved"]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.sagemaker_approval_rule.name
  target_id = "TriggerDeploymentLambda"
  arn       = aws_lambda_function.trigger_deployment.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_deployment.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.sagemaker_approval_rule.arn
}

resource "random_id" "secret_suffix" {
  byte_length = 4
}

resource "aws_secretsmanager_secret" "github_pat" {
  name                    = "github-pat-for-mlops-${random_id.secret_suffix.hex}"
  description             = "GitHub PAT for triggering repository_dispatch events"
  recovery_window_in_days = 0  # Allow immediate deletion and recreation
  
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_secretsmanager_secret_version" "github_pat_version" {
  secret_id     = aws_secretsmanager_secret.github_pat.id
  secret_string = var.github_pat # Pass the PAT from GitHub secrets
} 