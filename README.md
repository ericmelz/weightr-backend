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
Prerequisites: You need
[Helm](https://helm.sh/docs/intro/install/),
[jq](https://jqlang.org/),
[Docker](https://www.docker.com/products/docker-desktop/) and [k3d](https://k3d.io/stable/).

Set up a cluster containing Redis:
```bash
make infra
```

## Configure
```bash
make configure
```

### Run
```
make run
```
Visit <http://localhost:8088/docs>


## Local Docker setup
### Configure
Copy the configuration template:
```bash
cp var/conf/weightr-backend/.env.dev.docker.template var/conf/finquery/.env.dev.docker
```
Edit `var/conf/weightr-backend/.env.docker` with your values

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
rm -f var/conf/weightr-backend/.env.dev.template.docker.gpg
cat var/conf/weightr-backend/.env.docker|gpg --symmetric --cipher-alg AES256 --batch --passphrase "$GPG_PASSPHRASE" -o var/conf/weightr-backend/.env.dev.template.docker.gpg
```

Note: you can decrypt your conf using
```bash
gpg --batch --yes --passphrase "$GPG_PASSPHRASE" -o var/conf/weightr-backend/.env.dev.template.docker.decrypted -d var/conf/weightr-backend/.env.dev.template.docker.gpg                          
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
kubectl get pv,pvc,deployments,pods,middleware,ingress
```

### Access the service
visit http://localhost:8899/weightr-backend/docs

### Destroy cluster
```bash
k3d cluster delete weightr-backend
```



