provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = var.cluster_name
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_group_defaults = {
    ami_type = "AL2_x86_64"
  }

  eks_managed_node_groups = {
    one = {
      name           = "node-group-1"
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
    }
  }

  # This allows our GitHub Actions Role to interact with the cluster
  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.github_actions_role.arn
      username = "github-actions"
      groups   = ["system:masters"]
    }
  ]
  
  tags = {
    Terraform   = "true"
    Environment = "dev"
    Project     = "abalone-mlops"
  }
}

resource "helm_release" "mlflow" {
  name       = "mlflow"
  repository = "https://larribas.me/mlflow-helm-chart/"
  chart      = "mlflow"
  version    = "1.10.1"
  namespace  = "mlflow"
  create_namespace = true

  set {
    name  = "backend-store.postgres.host"
    value = aws_db_instance.mlflow_db.address
  }
  set {
    name  = "backend-store.postgres.port"
    value = aws_db_instance.mlflow_db.port
  }
  set {
    name  = "backend-store.postgres.user"
    value = aws_db_instance.mlflow_db.username
  }
  set {
    name  = "backend-store.postgres.password"
    value = random_password.db_password.result
  }
  set {
    name  = "backend-store.postgres.database"
    value = aws_db_instance.mlflow_db.db_name
  }
  set {
    name  = "default-artifact-root"
    value = "s3://${aws_s3_bucket.pipeline_artifacts.bucket}/mlflow"
  }
  set {
    name  = "service.type"
    value = "LoadBalancer"
  }
}

resource "kubernetes_secret" "db_credentials" {
  metadata {
    name = "db-credentials"
  }

  data = {
    endpoint = aws_db_instance.mlflow_db.endpoint
    password = random_password.db_password.result
  }

  type = "Opaque"
}

data "kubernetes_service" "mlflow_service" {
  depends_on = [helm_release.mlflow]

  metadata {
    name      = "mlflow"
    namespace = "mlflow"
  }
}

data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_id
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
} 