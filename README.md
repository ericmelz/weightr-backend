# weightr-backend
Backend for weightr, a smart weight loss tracking app

You can try the app at <https://emelz.ai/weightr/>

## Overview
This is the backend of the weightr app.  See the companion project at <https://github.com/ericmelz/weightr-frontend>
for more details.

## Project Structure
TBD

## Required Infrastructure
You need Redis - TBD

## Get the project
Find a suitable dir (such as `~/Data/code`) and:
```bash
cd ~/Data/code
rm -rf weightr-backend
git clone git@github.com:ericmelz/weightr-backend.git
cd weightr-backend
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
You may see warnings but they're generally harmless.

