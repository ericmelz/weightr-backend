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
make k3d
```

### Access the service
visit http://localhost:8880/weightr-backend/docs

### Destroy cluster
```bash
make destroy-k3d
```



