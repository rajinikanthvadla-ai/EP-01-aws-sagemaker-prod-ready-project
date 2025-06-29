provider "aws" {
  region = var.aws_region
}

data "aws_rds_engine_version" "postgresql" {
  engine = "postgres"
}

resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&'()*+,-./:;<=>?@[]^_`{|}~"
}

resource "aws_ecr_repository" "api_repository" {
  name = "abalone-prediction-api"
  
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "ui_repository" {
  name = "abalone-prediction-ui"
  
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_db_instance" "mlflow_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = data.aws_rds_engine_version.postgresql.version
  instance_class       = "db.t3.micro"
  db_name              = "mlflowdb"
  username             = "mlflow"
  password             = random_password.db_password.result
  skip_final_snapshot  = true
  publicly_accessible = true # For simplicity in this lab. In production, use private endpoints.
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

resource "aws_security_group" "db_sg" {
  name        = "mlflow-db-sg"
  description = "Allow all inbound traffic for MLflow DB" # Restrict in production

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow all IPs. Restrict in production.
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Add IAM Role definitions here later 