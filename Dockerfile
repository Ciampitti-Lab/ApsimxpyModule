FROM python:3.12-slim

# Install system dependencies for R and sf
RUN apt-get update && apt-get install -y \
    gdal-bin \ 
    libgdal-dev \ 
    build-essential \ 
    docker.io \ 
    libudunits2-dev \ 
    && rm -rf /var/lib/apt/lists/*
    

WORKDIR /workspace

# Python dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv notebook ipykernel

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY apsimxpy/ ./apsimxpy/
RUN pip install -e ./apsimxpy

RUN python -m ipykernel install --name=mi_entorno --display-name "Python (Docker)"

ENV PYTHONPATH=/workspace:$PYTHONPATH

EXPOSE 8888

CMD ["bash"]
