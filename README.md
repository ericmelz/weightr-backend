# weightr-backend
Backend for weightr, a smart weight loss tracking app

You can try the app at <https://emelz.ai/weightr/>

## Overview
This is the backend of the weightr app.  See the companion project at <https://github.com/ericmelz/weightr-frontend>
for more details.

## Project Structure
TBD

## Get the project
Find a suitable dir (such as `~/Data/code`) and:
```bash
cd ~/Data/code
rm -rf weightr-backend
git clone git@github.com:ericmelz/weightr-backend.git
cd weightr-backend
```

## Required Infrastructure
You need Redis - here's how to set it up if you don't already have it running locally.

### Create a new k3d cluster
Prerequisites: You need [Docker](https://www.docker.com/products/docker-desktop/) and [k3d](https://k3d.io/stable/).
```bash
k3d cluster create infra -p "6379:6379@loadbalancer"
```

### Install Redis
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis -f k8s-infra/redis-values.yaml
```

### Update your hosts file
```bash
sudo echo "127.0.0.1 redis.infra.localhost" >> /etc/hosts
```

### Test redis
#### Native: If you have redis-cli already installed
```bash
redis-cli -h redis.infra.localhost
SET foo bar
GET foo
^d
```

### Docker: If you don't want to use an installed redis-cli
```bash
docker run -it --rm redis redis-cli -h host.docker.internal -p 6379
SET foo bar
GET foo
```

## Local laptop native setup
### Install uv if it's not already on your system

```bash
pip install uv
```

### Create and activate a virtual environment
```bash
uv venv
```

### Install dependencies, including development dependencies
```bash
uv pip install -e ".[dev]"
```

### Configure
Copy the configuration template:
```bash
cp var/conf/weightr-backend/.env.dev var/conf/weightr-backend/.env
```
Edit `var/conf/weightr-backend/.env` with your values

### Run tests
```bash
uv run pytest
```
You may see warnings, but they're generally harmless.

### Start app
```
uv run -m uvicorn weightr_backend.main:app --reload --host 0.0.0.0 --port 8088
```
Visit <http://localhost:8088/docs>

## Local Docker setup
### Configure
Copy the configuration template:
```bash
cp var/conf/finquery/.env.dev.docker var/conf/finquery/.env.docker
```
Edit `var/conf/finquery/.env-docker` with your values

### Build and run the docker image
```bash
./run.sh
```

### Hit the app
visit <http://localhost:8088/docs>

## Local k3d setup
### Prerequisites
- Docker installed
- k3d installed (`curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash`)

### Record the configuration directory
```bash
VAR_DIR=$(pwd)/var
```
### Create a new k3d cluster
```bash
k3d cluster create weightr-backend -p "8899:80@loadbalancer" --volume "$VAR_DIR:/mnt/var@server:0"
```

### Encrypt the configuration
The kubernetes environment assumes that configuration exists as 
gpg-encrypted .env files on your file system.  Do not store unencrypted credentials on your
file system.

Create a GPG_PASSPHRASE:
```bash
export GPG_PASSPHRASE=$(openssl rand -base64 32)
```

Encrypt your credentials: 
```bash
rm -f var/conf/weightr-backend/.env.dev.docker.gpg
cat var/conf/weightr-backend/.env.docker|gpg --symmetric --cipher-alg AES256 --batch --passphrase "$GPG_PASSPHRASE" -o var/conf/weightr-backend/.env.dev.docker.gpg
```

Note: you can decrypt your conf using
```bash
gpg --batch --yes --passphrase "$GPG_PASSPHRASE" -o var/conf/weightr-backend/.env.dev.docker.decrypted -d var/conf/weightr-backend/.env.dev.docker.gpg                          
```

### Build the Docker image and import it into the cluster
```bash
docker build -t weightr-backend:latest .
k3d image import weightr-backend:latest -c weightr-backend
```

### Install the configuration encryption key
```bash
kubectl create secret generic gpg-passphrase --from-literal=GPG_PASSPHRASE=$GPG_PASSPHRASE
```

### Deploy to k3d
```bash
kubectl apply -f k8s/
```

### Verify deployment
```bash
kubectl get pv,pvc,deployments,pods,ingress
```

### Access the service
visit http://localhost:8899/weightr-backend/docs

### Destroy cluster
```bash
k3d cluster delete weightr-backend
```



