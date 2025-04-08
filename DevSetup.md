# Dev Setup
Here we assume you have a Mac.

## 1. 🔧 Install tools
```bash
brew install k3d helm redis
```
Install and run [Docker](https://docs.docker.com/desktop/setup/install/mac-install/).

### 2. 🧹 (Optional) Cleanup docker
```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker rmi -f $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network prune -f
```

### 3. 🚀 Create k3d cluster
```bash
k3d cluster create weightr-dev --agents 1
sed -i '' 's/host\.docker\.internal/127.0.0.1/g' ~/.config/k3d/kubeconfig-weightr-dev.yaml
KUBECONFIG=~/.config/k3d/kubeconfig-weightr-dev.yaml kubectl config view --flatten > ~/.kube/config
kubectl cluster-info
```

### 4. 📦 Install Redis and MySQL
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Redis
helm install redis bitnami/redis --set auth.enabled=false --set architecture=standalone --set master.persistence.enabled=true --create-namespace --namespace redis

# MySQL
helm install mysql bitnami/mysql \
  --set auth.rootPassword=my-root-pw \
  --set auth.database=weightr \
  --set primary.persistence.enabled=true \
  --create-namespace --namespace mysql
```

### 5. 🌐 Port-forward (in separate terminal) 
```bash
kubectl port-forward svc/redis-master 6379:6379 -n redis
kubectl port-forward svc/mysql 3306:3306 -n mysql
```

### 6. 🔬 Test Infrastructure
```bash
redis-cli
get foo
set foo bar
get foo
^D


```