provider "aws" {
  region = var.aws_region
}

data "aws_rds_engine_version" "postgresql" {
  engine = "postgres"
}

resource "random_password" "db_password" {
  length  = 16
  special = true
  # Only include safe special characters for RDS (exclude /, @, ", and space)
  override_special = "!#$%&()*+,-.:<=>?[]^_`{|}~"
}

resource "aws_ecr_repository" "api_repository" {
  name = "abalone-prediction-api"
  
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_ecr_repository" "ui_repository" {
  name = "abalone-prediction-ui"
  
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_db_instance" "mlflow_db" {
  identifier           = "mlflow-database"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = data.aws_rds_engine_version.postgresql.version
  instance_class       = "db.t3.micro"
  db_name              = "mlflowdb"
  username             = "mlflow"
  password             = random_password.db_password.result
  skip_final_snapshot  = true
  delete_automated_backups = true
  publicly_accessible = true # For simplicity in this lab. In production, use private endpoints.
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name = aws_db_subnet_group.mlflow_db_subnet_group.name

  lifecycle {
    prevent_destroy = false
  }

  depends_on = [
    aws_security_group.db_sg,
    aws_db_subnet_group.mlflow_db_subnet_group
  ]
}

resource "aws_db_subnet_group" "mlflow_db_subnet_group" {
  name       = "mlflow-db-subnet-group"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "MLflow DB subnet group"
  }
}

resource "aws_security_group" "db_sg" {
  name        = "mlflow-db-sg"
  description = "Allow PostgreSQL traffic for MLflow DB"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block] # Allow VPC traffic
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow all IPs for simplicity in lab
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "MLflow Database Security Group"
  }
}

# Add IAM Role definitions here later 