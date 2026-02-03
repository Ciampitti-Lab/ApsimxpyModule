# 
APSIM NG simulations in Python-


# apsimxpy-APSIMNG-Python

APSIM NG simulations in Python. Workflow Included. 

## 📦 Installation

### Prerequisites
- docker
- apsiminitiative/apsimng (docker image)

### Steps

- Clone Repository
- Run following commands in your terminal
```bash
  - docker build -t apsimxpy .
  - docker compose up -d
```
## 📂 Module Structure

apsimxpy/
├── __init__.py
├── weather.py
├── clock.py
├── helptree.py
├── microclimate.py
├── pyproject.toml
├── utils.py
└── field/
    ├── __init__.py
    ├── surfaceorganicmatter.py 
    ├── management/ 
    │    ├── __init__.py 
    │    └── fertilize.py
    └── soil/
        ├── __init__.py
        ├── chemical.py
        ├── organic.py
        ├── physical.py
        ├── soil_water.py
        ├── water.py
        └── ssurgo/
            ├── saxton.py
            ├── sdainterp.py
            ├── sdapoly.py
            ├── sdaprop.py
            ├── soil_apsim.py
            └── soil_extraction.py

## 🚀 Features
- apsimxpy module (APSIM NG simulations in Python)
- workflow using apsimxpy


