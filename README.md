# CLO835 Assignment 2: Kubernetes Deployment on AWS Cloud9

## Overview
This project demonstrates deploying a containerized Flask web application and MySQL database on a single-node Kubernetes cluster using kind, running on an AWS EC2 instance (Cloud9). The application allows adding and retrieving employee information.

---

## Table of Contents
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Kubernetes Manifests](#kubernetes-manifests)
- [Deployment Steps](#deployment-steps)
- [Testing](#testing)
- [Rolling Update](#rolling-update)
- [Assignment Questions & Answers](#assignment-questions--answers)
- [Challenges & Solutions](#challenges--solutions)
- [References](#references)

---

## Project Structure
```
k8s/                  # All Kubernetes manifests (pods, replicasets, deployments, services)
scripts/              # Deployment, update, and cleanup scripts
templates/            # Flask HTML templates
terraform/            # (Optional) Terraform files for infra
app.py                # Flask application
Dockerfile            # Flask app Dockerfile
Dockerfile_mysql      # MySQL Dockerfile (if used)
mysql.sql             # MySQL init script
requirements.txt      # Python dependencies
README.md             # This file
```

---

## Prerequisites
- AWS Cloud9 environment (Amazon Linux, t3.medium or larger, 40GB+ disk)
- Docker, kind, kubectl installed
- GitHub account

---

## Setup Instructions
1. **Clone this repo in Cloud9:**
   ```bash
git clone <your-repo-url>
cd <repo>
   ```
2. **Install prerequisites:**
   ```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
   ```
3. **Log out and log back in to apply Docker group changes.**
4. **Build the Docker image:**
   ```bash
docker build -t my_app:latest -f Dockerfile .
   ```
5. **Create kind cluster with NodePort mapping:**
   ```bash
kind create cluster --name clo835-cluster --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
    protocol: TCP
EOF
   ```
6. **Load the image into kind:**
   ```bash
kind load docker-image my_app:latest --name clo835-cluster
   ```

---

## Kubernetes Manifests
- **Pod, ReplicaSet, Deployment, and Service** manifests for both MySQL and the web app are in the `k8s/` directory.
- The web app is exposed via NodePort 30000; MySQL is exposed via ClusterIP.

---

## Deployment Steps
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mysql-configmap.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/mysql-service.yaml
kubectl wait --for=condition=available --timeout=300s deployment/mysql-deployment -n clo835-app
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml
kubectl wait --for=condition=available --timeout=300s deployment/app-deployment -n clo835-app
```

---

## Testing
- **Browser:** Go to `http://<EC2-PUBLIC-IP>:30000` to access the app.
- **EC2/Cloud9 terminal:**
  ```bash
  curl http://localhost:30000
  ```
- **Add and retrieve employee data to verify full functionality.**

---

## Rolling Update
1. Edit `app.py` (change version string or feature).
2. Rebuild and reload the image:
   ```bash
   docker build -t my_app:v2 .
   kind load docker-image my_app:v2 --name clo835-cluster
   ```
3. Update the deployment:
   ```bash
   kubectl set image deployment/app-deployment flask-app=my_app:v2 -n clo835-app
   kubectl rollout status deployment/app-deployment -n clo835-app
   ```
4. Verify the new version is running in the browser or with `kubectl`.

---

## Assignment Questions & Answers

**1. What is the IP of the K8s API server in your cluster?**
- Run `kubectl cluster-info` and copy the API server IP (e.g., `https://172.18.0.2:6443`).

**2. Can both applications listen on the same port inside the container?**
- Yes, because each pod has its own network namespace and IP address, so there is no port conflict.

**3. Is the pod created in step 2 governed by the ReplicaSet you created?**
- No, only pods created by the ReplicaSet controller are governed by it. Pods created directly are not managed by ReplicaSets.

**4. Is the ReplicaSet created in step 3 part of this deployment?**
- No, Deployments create and manage their own ReplicaSets. The manually created ReplicaSet is independent.

**5. Why use different service types for web and MySQL?**
- The web app uses NodePort to allow external access. MySQL uses ClusterIP to restrict access to within the cluster for security.

---

## Challenges & Solutions
- **Disk/memory issues:** Resized Cloud9 EBS volume and pruned Docker images.
- **NodePort not accessible:** Ensured kind cluster was created with correct port mapping and security group allowed port 30000.
- **App couldn't connect to MySQL:** Fixed by matching environment variables and restarting pods after MySQL was ready.
- **Flask/Werkzeug compatibility:** Pinned compatible versions in `requirements.txt`.
- **MySQL auth plugin error:** Added `cryptography` to requirements.

---

## References
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Flask Docs](https://flask.palletsprojects.com/)
- [MySQL Docker Docs](https://hub.docker.com/_/mysql)
- [AWS Cloud9 Docs](https://docs.aws.amazon.com/cloud9/)

---

## Sample Commit Message
```bash
git add README.md
git commit -m "Add comprehensive README with setup, deployment, testing, and assignment answers"
git push
``` 