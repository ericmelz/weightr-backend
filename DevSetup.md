# Dev Setup
Here we assume you have a Mac.

## 1. 🔧 Install tools
```bash
brew install k3d helm redis mysql
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
export MYSQL_ROOT_PASSWORD=YOUR_PASSWORD_GOES_HERE
helm install mysql bitnami/mysql \
  --set auth.rootPassword=$MYSQL_ROOT_PASSWORD \
  --set auth.database=weightr \
  --set primary.persistence.enabled=true \
  --create-namespace --namespace mysql
```

### 5. 🌐 Port-forward (in separate terminals) 
```bash
kubectl port-forward svc/redis-master 6379:6379 -n redis
kubectl port-forward svc/mysql 3307:3306 -n mysql
```

### 6. 🔬 Test Infrastructure
```bash
redis-cli
get foo
set foo bar
get foo
^D

mysql -P3307 -h127.0.0.1 -uroot -p"$MYSQL_ROOT_PASSWORD"
show databases;
^D
```

### 7. 📦 (optional) Deploy Loki and Grafana
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install loki grafana/loki-stack \
  --namespace logging --create-namespace \
  --set grafana.enabled=false \
  --set prometheus.enabled=false

helm upgrade --install grafana grafana/grafana \
  --namespace logging \
  --set adminPassword='admin' \
  --set service.type=NodePort

export GRAFANA_ADMIN_PASSWORD=$(kubectl get secret --namespace logging grafana -o jsonpath="{.data.admin-password}" | base64 --decode) 
echo $GRAFANA_ADMIN_PASSWORD
```
### 8. 🌐 (optional) Port forward Grafana In separate terminal
```bash
kubectl port-forward svc/grafana -n logging 3000:80

```
* Visit http://localhost:3000
* Login is admin/admin

### 9. 🌐 (optional) Port forward Loki In separate terminal
```bash
kubectl port-forward svc/loki -n logging 3100:3100
```

Visit http://localhost:3100/loki/api/v1/labels

### 10. 📦 (optional) Deploy Promtail
```
docker run --rm -v /Users/ericmelz/Data/logs:/logs \
  -v $(pwd)/conf/promtail.yaml:/etc/promtail/config.yaml \
  grafana/promtail:2.9.3 \
  -config.file=/etc/promtail/config.yaml
```

### 11. 🎨 Connect Grafana to Loki
1. Add Loki as a data source (http://loki:3100).  
1. Go to Grafana Explore and query:
```logql
{job="weightr-backend"}
```