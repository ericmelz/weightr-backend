# Dev Setup
Here we assume you have a Mac.

## 1. Install tools
```bash
brew install k3d helm
```

### 2. Create k3d cluster
```bash
k3d cluster create weightr-dev --agents 1
```
