# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.project_name
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = concat(module.vpc.private_subnets, module.vpc.public_subnets)
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy,
  ]
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = module.vpc.private_subnets

  capacity_type  = "ON_DEMAND"
  instance_types = ["t3.medium"]

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
}

# Helm provider configuration
provider "helm" {
  kubernetes {
    host                   = aws_eks_cluster.main.endpoint
    cluster_ca_certificate = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.main.name]
    }
  }
}

# Kubernetes provider configuration  
provider "kubernetes" {
  host                   = aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", aws_eks_cluster.main.name]
  }
}

# Create MLflow namespace
resource "kubernetes_namespace" "mlflow" {
  metadata {
    name = "mlflow"
  }
  depends_on = [aws_eks_node_group.main]
}

# MLflow Helm Chart from Bitnami
resource "helm_release" "mlflow" {
  name       = "mlflow"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "mlflow"
  namespace  = kubernetes_namespace.mlflow.metadata[0].name
  version    = "0.7.19"

  set {
    name  = "tracking.auth.enabled"
    value = "false"
  }

  set {
    name  = "postgresql.enabled"
    value = "false"
  }

  set {
    name  = "externalDatabase.host"
    value = aws_db_instance.mlflow_db.address
  }

  set {
    name  = "externalDatabase.port"
    value = "5432"
  }

  set {
    name  = "externalDatabase.database"
    value = aws_db_instance.mlflow_db.db_name
  }

  set {
    name  = "externalDatabase.user"
    value = aws_db_instance.mlflow_db.username
  }

  set_sensitive {
    name  = "externalDatabase.password"
    value = aws_db_instance.mlflow_db.password
  }

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "service.annotations.service\\.beta\\.kubernetes\\.io/aws-load-balancer-type"
    value = "nlb"
  }

  depends_on = [
    aws_eks_node_group.main,
    aws_db_instance.mlflow_db,
    kubernetes_namespace.mlflow
  ]
}

# Get MLflow service details
data "kubernetes_service" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.mlflow.metadata[0].name
  }
  depends_on = [helm_release.mlflow]
}

data "aws_eks_cluster" "cluster" {
  name = var.cluster_name
}

data "aws_eks_cluster_auth" "cluster" {
  name = var.cluster_name
} 