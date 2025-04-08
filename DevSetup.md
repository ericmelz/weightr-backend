# Dev Setup
Here we assume you have a Mac.

## 1. Install tools
```bash
brew install k3d helm
```
Install and run [Docker](https://docs.docker.com/desktop/setup/install/mac-install/).

### 2. (Optional) Cleanup docker
```bash
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
docker rmi -f $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network prune -f
```

### 3. Create k3d cluster
```bash
k3d cluster create weightr-dev --agents 1
```
